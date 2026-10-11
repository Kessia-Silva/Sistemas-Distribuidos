
import random
import threading
import time

import Pyro5.api

from configuracao import Configuracao
from relogioVetorial import RelogioVetorial
from evento import Evento
from logger import Logger


@Pyro5.api.expose
class Processo:

    def __init__(self, nome):
        self.nome = nome.lower()

        self.relogio = RelogioVetorial(
            Configuracao.PROCESSOS,
            self.nome
        )

        self.logger = Logger(self.nome)

        # Contador único para os eventos registrados neste processo.
        self.numero_evento = 0

        # Armazena as URIs dos outros processos.
        self.processos = {}

        # Protege o relógio, o contador e a lista de processos.
        self.lock = threading.RLock()

        self.inicio = time.time()

        print(f"[{self.nome}] Processo criado.")

    def _proximo_numero_evento(self):
        """Deve ser chamado com self.lock adquirido."""
        self.numero_evento += 1
        return self.numero_evento

    def descobrir_processos(self):
        """Consulta o Name Server e atualiza as URIs conhecidas."""
        try:
            ns = Pyro5.api.locate_ns()

            encontrados = {}

            for nome_processo in Configuracao.PROCESSOS:
                if nome_processo == self.nome:
                    continue

                try:
                    uri = ns.lookup(f"processo.{nome_processo}")
                    encontrados[nome_processo] = uri
                except Exception:
                    # O outro processo pode ainda não ter iniciado.
                    continue

            with self.lock:
                self.processos.update(encontrados)

            return True

        except Exception as erro:
            print(
                f"[{self.nome}] Não foi possível consultar "
                f"o Name Server: {erro}"
            )
            return False

    def receber_mensagem(
        self,
        processo_origem,
        numero_evento,
        relogio_recebido
    ):
        """
        Método remoto chamado quando uma mensagem chega.
        O relógio recebido corresponde ao evento de envio.
        """
        with self.lock:
            novo_relogio = self.relogio.receber_mensagem(
                relogio_recebido
            )

            numero_recebimento = self._proximo_numero_evento()

            evento = Evento(
                processo=self.nome,
                numero=numero_recebimento,
                tipo="RECEBIMENTO",
                instante=Evento.agora(),
                relogio=novo_relogio,
                origem=processo_origem,
                evento_origem=numero_evento
            )

            self.logger.registrar(evento)

        return True

    def _enviar_mensagem(
        self,
        destino,
        uri_destino,
        numero_evento_origem,
        numero_evento_envio,
        relogio_envio
    ):
        """
        Executado em uma thread separada para que o atraso
        de uma mensagem não bloqueie a geração de eventos.
        """
        delay = random.uniform(
            Configuracao.DELAY_MIN,
            Configuracao.DELAY_MAX
        )

        time.sleep(delay)

        try:
            with Pyro5.api.Proxy(uri_destino) as proxy:
                proxy.receber_mensagem(
                    self.nome,
                    numero_evento_envio,
                    relogio_envio
                )

            print(
                f"[{self.nome}] Mensagem do evento local "
                f"E{numero_evento_origem} enviada para {destino} "
                f"| evento de envio=E{numero_evento_envio} "
                f"| delay={delay:.3f}s",
                flush=True
            )

        except Exception as erro:
            print(
                f"[{self.nome}] Erro ao enviar para "
                f"{destino}: {erro}",
                flush=True
            )

    def gerar_evento(self):
        """Registra um evento local e dissemina a informação."""
        with self.lock:
            # 1. Evento local.
            novo_relogio = self.relogio.evento_local()
            numero_local = self._proximo_numero_evento()

            evento_local = Evento(
                processo=self.nome,
                numero=numero_local,
                tipo="LOCAL",
                instante=Evento.agora(),
                relogio=novo_relogio
            )

            self.logger.registrar(evento_local)

            # Copia os destinos e suas URIs conhecidas.
            destinos = list(self.processos.items())

            # 2. Registra um evento de envio para cada destinatário.
            envios = []

            for destino, uri_destino in destinos:
                relogio_envio = self.relogio.evento_local()
                numero_envio = self._proximo_numero_evento()

                evento_envio = Evento(
                    processo=self.nome,
                    numero=numero_envio,
                    tipo="ENVIO",
                    instante=Evento.agora(),
                    relogio=relogio_envio,
                    destino=destino,
                    evento_origem=numero_local
                )

                self.logger.registrar(evento_envio)

                envios.append(
                    (
                        destino,
                        uri_destino,
                        numero_local,
                        numero_envio,
                        relogio_envio
                    )
                )

        # 3. Inicia os envios fora do lock.
        # Cada destino possui seu próprio atraso e sua própria thread.
        for dados in envios:
            thread = threading.Thread(
                target=self._enviar_mensagem,
                args=dados,
                daemon=True
            )
            thread.start()

    def executar_eventos(self):
        """Gera eventos em intervalos aleatórios durante o experimento."""
        print(
            f"[{self.nome}] Iniciando geração de eventos "
            f"por {Configuracao.DURACAO} segundos."
        )

        while (
            time.time() - self.inicio
            < Configuracao.DURACAO
        ):
            # Descobre processos que já estejam registrados.
            self.descobrir_processos()

            intervalo = random.uniform(
                Configuracao.INTERVALO_MIN,
                Configuracao.INTERVALO_MAX
            )

            # Evita iniciar um novo evento depois do limite.
            tempo_restante = (
                Configuracao.DURACAO - (time.time() - self.inicio)
            )

            if tempo_restante <= 0:
                break

            time.sleep(min(intervalo, tempo_restante))

            if (
                time.time() - self.inicio
                >= Configuracao.DURACAO
            ):
                break

            self.descobrir_processos()
            self.gerar_evento()

        print(
            f"[{self.nome}] Geração de eventos encerrada."
        )


if __name__ == "__main__":
    nome = input(
        "Digite o nome do processo (P1, P2, P3 ou P4): "
    ).strip().lower()

    if nome not in Configuracao.PROCESSOS:
        print("Nome inválido. Use P1, P2, P3 ou P4.")
        raise SystemExit(1)

    processo = Processo(nome)

    daemon = Pyro5.api.Daemon()
    uri = daemon.register(processo)

    ns = Pyro5.api.locate_ns()
    ns.register(f"processo.{nome}", uri)

    print()
    print("=" * 55)
    print(f"PROCESSO {nome.upper()} INICIADO")
    print(f"URI: {uri}")
    print("=" * 55)

    # A geração de eventos ocorre em paralelo com o atendimento
    # das chamadas remotas do Pyro5.
    thread_eventos = threading.Thread(
        target=processo.executar_eventos,
        daemon=True
    )
    thread_eventos.start()

    try:
        # Mantém o processo disponível durante a geração e por
        # alguns segundos extras para receber mensagens pendentes.
        limite = (
            processo.inicio
            + Configuracao.DURACAO
            + Configuracao.MARGEM_FINAL
        )

        daemon.requestLoop(
            loopCondition=lambda: time.time() < limite
        )

    finally:
        try:
            ns.remove(f"processo.{nome}")
        except Exception:
            pass

        daemon.close()
        print(f"[{nome}] Processo encerrado.")
