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

        # Nome do processo.
        self.nome = nome

        # relogio Vetorial
        self.relogio = RelogioVetorial(
            Configuracao.PROCESSOS,
            nome
        )

        # Logger
        self.logger = Logger(nome)

        # Contador de eventos
        self.numero_evento = 0

        # Armazenamento das URIs dos processos
        self.processos = {}

        # O lock protege as estruturas compartilhadas entre as threads. 
        self.lock = threading.Lock()

        # Inicio do processo
        self.inicio = time.time()

        print(
            f"[{self.nome}] Processo criado."
        )

    # Receber menssagem
    def receber_mensagem(
        self,
        processo_origem,
        numero_evento,
        relogio_recebido
    ):

        # Metodo chamado remotamente: representa o evento de Recebimento
        with self.lock:

            # Atualiza o relógio vetorial usando o relógio recebido.
            novo_relogio = (
                self.relogio.receber_mensagem(
                    relogio_recebido
                )
            )

            # Cria um novo número para o evento.
            self.numero_evento += 1

            # Cria o evento de recebimento.
            evento = Evento(
                processo=self.nome,
                numero=self.numero_evento,
                tipo="RECEBIMENTO",
                instante=Evento.agora(),
                relogio=novo_relogio,
                origem=processo_origem
            )

            # Salva o evento no log.
            self.logger.registrar(evento)

            print(
                f"[{self.nome}] "
                f"RECEBEU evento "
                f"{numero_evento} "
                f"de {processo_origem} "
                f"| relógio={novo_relogio}"
            )

        return True

    # Procura no NameServer pelos outros processos.
    def descobrir_processos(self):

        # Localiza o NameServer.
        ns = Pyro5.api.locate_ns()

        encontrados = {}

        # Percorre P1, P2, P3 e P4.
        for processo in Configuracao.PROCESSOS:

            # Não precisamos procurar pelo próprio processo.
            if processo == self.nome:
                continue

            try:

                # Procura o processo no NameServer.
                uri = ns.lookup(
                    f"processo.{processo}"
                )

                # Guarda a URI encontrada.
                encontrados[processo] = uri

            except Exception:
                # Caso o processo ainda não esteja disponível, simplesmente continua.
                pass

        # Atualiza a lista de processos.
        with self.lock:
            self.processos = encontrados

        return True

    # Envia uma mensagem para outro processo.
    def enviar_mensagem(
        self,
        destino,
        numero_evento,
        relogio_evento
    ):

        # delay aleatorio
        delay = random.uniform(
            Configuracao.DELAY_MIN,
            Configuracao.DELAY_MAX
        )

        # Simula o tempo de trânsito da mensagem.
        time.sleep(delay)

        try:

            # Cria uma conexão com o processo destino.
            with Pyro5.api.Proxy(
                self.processos[destino]
            ) as proxy:

                # Chama remotamente o método receber_mensagem().
                proxy.receber_mensagem(
                    self.nome,
                    numero_evento,
                    relogio_evento
                )

            print(
                f"[{self.nome}] "
                f"mensagem enviada para {destino} "
                f"| delay={delay:.3f}s"
            )

        except Exception as erro:

            print(
                f"[{self.nome}] "
                f"erro ao enviar para {destino}: "
                f"{erro}"
            )

    # Gera um novo evento local
    def gerar_evento(self):

        with self.lock:

            # Atualiza o relógio vetorial.
            novo_relogio = (
                self.relogio.evento_local()
            )

            # Incrementa o número do evento.
            self.numero_evento += 1

            numero = self.numero_evento

            # Cria o evento.
            evento = Evento(
                processo=self.nome,
                numero=numero,
                tipo="LOCAL",
                instante=Evento.agora(),
                relogio=novo_relogio
            )

            # Salva no log.
            self.logger.registrar(evento)

        print(
            f"[{self.nome}] "
            f"EVENTO LOCAL {numero} "
            f"| relógio={novo_relogio}"
        )

        # Cria uma thread para cada destino.
        for destino in list(
            self.processos.keys()
        ):

            thread = threading.Thread(
                target=self.enviar_mensagem,
                args=(
                    destino,
                    numero,
                    novo_relogio
                ),
                daemon=True
            )

            thread.start()

    # Gera eventos durante o período definido na configuração.

    def executar_eventos(self):

        print(
            f"[{self.nome}] "
            f"Iniciando geração de eventos..."
        )

        # Continua enquanto não atingir o tempo máximo do experimento.
        while (
            time.time() - self.inicio
            < Configuracao.DURACAO
        ):

            # Escolhe um intervalo aleatório.
            intervalo = random.uniform(
                Configuracao.INTERVALO_MIN,
                Configuracao.INTERVALO_MAX
            )

            # Espera antes do próximo evento.
            time.sleep(intervalo)

            # Atualiza a lista dos processos.
            self.descobrir_processos()

            # Gera o evento local.
            self.gerar_evento()

        print(
            f"[{self.nome}] "
            f"Tempo de execução encerrado."
        )


if __name__ == "__main__":

    # Escolher processo
    nome = input(
        "Digite o nome do processo (P1, P2, P3 ou P4): "
    ).strip().upper()

    # Verifica se o nome é válido.
    if nome not in Configuracao.PROCESSOS:

        print(
            "Nome inválido."
        )

        print(
            "Use P1, P2, P3 ou P4."
        )

        exit()

    # Cria processo
    processo = Processo(nome)

    daemon = Pyro5.api.Daemon()

    # Registra o objeto no daemon.
    uri = daemon.register(processo)

    ns = Pyro5.api.locate_ns()

    # Registrar processo
    ns.register(
        f"processo.{nome}",
        uri
    )

    # Mostrar informações
    print()
    print("=" * 50)
    print(
        f"PROCESSO {nome} INICIADO"
    )
    print("=" * 50)
    print(
        f"URI: {uri}"
    )
    print()

    # Thread dos eventos
    thread_eventos = threading.Thread(
        target=processo.executar_eventos,
        daemon=True
    )

    thread_eventos.start()

    daemon.requestLoop()

