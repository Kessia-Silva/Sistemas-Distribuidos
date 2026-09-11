"""
Created on Wed Sep  9 14:45:37 2026
@author: massa
"""
import Pyro5.api
import threading
import time

# ==========================================
# 1. OBJETO DISTRIBUÍDO DO JOGADOR
# ==========================================
@Pyro5.api.expose
class Jogador:
    def __init__(self):
        # SISTEMA DE SINCRONIZAÇÃO DE DUPLO EVENTO (Semáforos binários):
        # Sinaliza para a Main Thread (CLI) que é o momento de ler o teclado.
        self.turno_evento = threading.Event()
        # Sinaliza para a Thread de Rede (Pyro) que o input do teclado foi concluído.
        self.jogada_evento = threading.Event()
        self.resposta_evento = threading.Event()
        self.responder_evento = threading.Event()
        # Sinaliza para a Main Thread que a partida terminou
        # e que é o momento de perguntar se o jogador deseja continuar.
        self.partida_terminou_evento = threading.Event()
        self.resposta = ""
        self.jogada = None
        self.jogo_ativo = True

    # O decorador @oneway avisa ao middleware que o servidor não precisa
    # aguardar um "return". É o equivalente a mensagens UDP (fire-and-forget),
    # otimizando a responsividade geral do sistema.
    @Pyro5.api.oneway
    def receber_mensagem(self, msg):
        print(msg)

    def responder(self):
        # Limpa o evento antes de começar uma nova solicitação.
        self.resposta_evento.clear()
        # Avisa a Main Thread que precisa pedir uma informação ao usuário.
        self.responder_evento.set()
        self.turno_evento.set()
        # A Thread do Pyro fica esperando até a Main Thread receber
        # o nome e sinalizar que a resposta está pronta.
        self.resposta_evento.wait()
        return self.resposta

    @Pyro5.api.oneway
    def partida_terminou(self):
        # O servidor chama este método quando a partida terminar.
        # A Main Thread será acordada para perguntar ao jogador
        # se ele deseja iniciar/continuar outra partida.
        self.partida_terminou_evento.set()
        self.turno_evento.set()

    @Pyro5.api.oneway
    def finalizar(self):
        self.jogo_ativo = False
        # Se a Main Thread estiver dormindo esperando um turno,
        # precisamos acordá-la para que ela perceba que o jogo acabou
        # e encerre o programa.
        self.turno_evento.set()

    def fazer_jogada(self):
        # Esta função é executada DENTRO DA THREAD SECUNDÁRIA criada pelo Pyro,
        # gerada quando o servidor faz o Remote Procedure Call (RPC).
        self.jogada_evento.clear()
        # Acorda o loop principal (CLI), que estava suspenso.
        self.turno_evento.set()
        # Bloqueia esta thread de rede especificamente, impedindo que o Pyro
        # devolva o controle ao servidor até que o usuário digite a jogada.
        self.jogada_evento.wait()
        # Retorna a jogada pela rede ao servidor.
        return self.jogada


# ==========================================
# 2. INTERFACE E LOOP PRINCIPAL (MAIN THREAD)
# ==========================================
def enviar_heartbeat(servidor, jogador_uri, jogador):
    while jogador.jogo_ativo:
        try:
            servidor.heartbeat(str(jogador_uri))
        except Exception:
            pass

        time.sleep(5)


def main():
    try:
        # Busca no Name Server o endereço remoto do Servidor Principal.
        ns = Pyro5.api.locate_ns()
        uri = ns.lookup("jogodavelha.servidor")
        servidor = Pyro5.api.Proxy(uri)
    except Exception as e:
        print("Erro ao localizar o servidor. O Name Server está rodando?", e)
        return

    # Registra este cliente na rede Pyro para que o Servidor
    # possa invocar seus métodos.
    jogador = Jogador()
    daemon = Pyro5.api.Daemon()
    jogador_uri = daemon.register(jogador)

    # Inicia a escuta de chamadas do servidor em uma thread em background.
    # Se não fizéssemos isso numa thread separada, o requestLoop()
    # travaria o código e nunca chegaríamos na parte do input().
    threading.Thread(
        target=daemon.requestLoop,
        daemon=True
    ).start()

    print("Conectando ao servidor... Aguardando um adversário entrar na fila.")

    # Chama o método remoto do servidor, passando o endereço do próprio cliente.
    servidor.iniciar_jogo(str(jogador_uri))

    # Inicia o envio periódico de heartbeat para o servidor.
    threading.Thread(
        target=enviar_heartbeat,
        args=(servidor, jogador_uri, jogador),
        daemon=True
    ).start()

    try:
        # Loop do CLI (Command Line Interface).
        # Esta é a única thread que interage diretamente com sys.stdin (teclado).
        while jogador.jogo_ativo:
            # A thread entra em estado "SUSPENDED" (não gasta processamento)
            # até que alguma thread do Pyro mude o estado do Evento para set().
            jogador.turno_evento.wait()

            # Reseta o evento para o próximo ciclo.
            jogador.turno_evento.clear()

            # ==========================================
            # PARTIDA TERMINOU
            # ==========================================
            if jogador.partida_terminou_evento.is_set():
                jogador.partida_terminou_evento.clear()

                # O CLIENTE apenas pergunta ao jogador.
                # Ele não decide se haverá revanche.
                resposta = input(
                    "A partida terminou. Deseja continuar? "
                )

                # Envia a resposta ao SERVIDOR.
                #
                # O servidor é responsável por:
                # 1. guardar a resposta deste jogador;
                # 2. esperar o outro jogador responder;
                # 3. decidir se haverá uma nova partida.
                if jogador.jogo_ativo:
                    servidor.responder_revanche(
                        str(jogador_uri),
                        resposta
                    )

                continue

            # ==========================================
            # PEDIDO DE NOME
            # ==========================================
            if jogador.responder_evento.is_set():
                jogador.resposta = input("Digite seu nome: ")
                jogador.responder_evento.clear()
                jogador.resposta_evento.set()
                continue

            # ==========================================
            # FINALIZAÇÃO
            # ==========================================
            if not jogador.jogo_ativo:
                print("\nEncerrando o cliente...")
                break

            # ==========================================
            # JOGADA
            # ==========================================
            print(">>> É a sua vez!")

            # Loop de validação de entrada.
            while True:
                try:
                    linha = int(input("Linha (0-2): "))
                    coluna = int(input("Coluna (0-2): "))

                    # Validação no cliente.
                    # O servidor também valida, garantindo a segurança da regra.
                    if 0 <= linha <= 2 and 0 <= coluna <= 2:
                        jogador.jogada = (linha, coluna)
                        break
                    else:
                        print(
                            "Por favor, digite valores válidos entre 0 e 2."
                        )
                except ValueError:
                    print(
                        "Entrada inválida. Digite apenas números inteiros."
                    )

            # Avisa à thread do Pyro que os dados estão prontos.
            # O .wait() dentro de fazer_jogada() é destravado.
            jogador.jogada_evento.set()

    except KeyboardInterrupt:
        # Captura CTRL+C garantindo que o programa feche
        # sem estourar Tracebacks feios.
        print("\nDesconectado pelo jogador.")

        # Avisa ao servidor que este jogador saiu voluntariamente.
        try:
            servidor.desconectar(str(jogador_uri))
        except Exception:
            pass

        jogador.jogo_ativo = False


if __name__ == "__main__":
    main()