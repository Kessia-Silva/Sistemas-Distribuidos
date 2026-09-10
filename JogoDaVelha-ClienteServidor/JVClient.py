"""
Created on Wed Sep  9 14:45:37 2026
@author: massa
"""
import Pyro5.api
import threading

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
     self.resposta_evento.clear()

     self.responder_evento.set()
     self.turno_evento.set()

     self.resposta_evento.wait()

     return self.resposta

    @Pyro5.api.oneway
    def finalizar(self):
        self.jogo_ativo = False
        # Se a Main Thread estiver dormindo esperando um turno, precisamos acordá-la
        # para que ela perceba que o jogo acabou e encerre o programa.
        self.turno_evento.set() 

    def fazer_jogada(self):
        # Esta função é executada DENTRO DA THREAD SECUNDÁRIA criada pelo Pyro,
        # gerada quando o servidor faz o Remote Procedure Call (RPC).
        
        self.jogada_evento.clear() # "Abaixa" a bandeira de jogada pronta
        
        # 1. Acorda o loop principal (CLI), que estava suspenso (consumindo 0% de CPU).
        self.turno_evento.set()
        
        # 2. Bloqueia esta thread de rede especificamente, impedindo que o Pyro 
        # devolva o controle ao servidor até que o usuário digite a jogada no terminal.
        self.jogada_evento.wait() 
        
        return self.jogada # Retorna a tupla pela rede ao servidor

# ==========================================
# 2. INTERFACE E LOOP PRINCIPAL (MAIN THREAD)
# ==========================================
def main():
    try:
        # Busca no Name Server o endereço de memória remoto do Servidor Principal
        ns = Pyro5.api.locate_ns()
        uri = ns.lookup("jogodavelha.servidor")
        servidor = Pyro5.api.Proxy(uri)
    except Exception as e:
        print("Erro ao localizar o servidor. O Name Server está rodando?", e)
        return

    # Registra este cliente na rede Pyro para que o Servidor possa invocar seus métodos
    jogador = Jogador()
    daemon = Pyro5.api.Daemon()
    jogador_uri = daemon.register(jogador)

    # Inicia a escuta de chamadas do servidor em uma thread em background (Daemon).
    # Se não fizéssemos isso numa thread separada, o requestLoop() travaria o código
    # e nunca chegaríamos na parte do input() do usuário.
    threading.Thread(target=daemon.requestLoop, daemon=True).start()



    print("Conectando ao servidor... Aguardando um adversário entrar na fila.")
    # Chama o método remoto do servidor, passando o endereço do próprio cliente
    servidor.iniciar_jogo(str(jogador_uri))

    try:
        # Loop do CLI (Command Line Interface). 
        # Esta é a única thread que interage diretamente com sys.stdin (teclado).
        while jogador.jogo_ativo:
            
            # A thread entra em estado "SUSPENDED" (não gasta processamento) 
            # até que a thread do Pyro mude o estado do Evento para set().
            jogador.turno_evento.wait() 
            jogador.turno_evento.clear() # Reseta o evento para o próximo ciclo

            if jogador.responder_evento.is_set():
             jogador.resposta = input("Digite seu nome: ")
             jogador.responder_evento.clear()
             jogador.resposta_evento.set()
             continue
            
            if not jogador.jogo_ativo:
                print("\nEncerrando o cliente...")
                break # Sai do while e finaliza o processo graciosamente
            
            print(">>> É a sua vez!")
            
            # Loop de validação de entrada
            while True:
                try:
                    linha = int(input("Linha (0-2): "))
                    coluna = int(input("Coluna (0-2): "))
                    
                    # Validação dupla (cliente e servidor) evita envios desnecessários pela rede
                    if 0 <= linha <= 2 and 0 <= coluna <= 2:
                        jogador.jogada = (linha, coluna)
                        break
                    else:
                        print("Por favor, digite valores válidos entre 0 e 2.")
                except ValueError:
                    print("Entrada inválida. Digite apenas números inteiros.")
            
            # Avisa à thread do Pyro que os dados estão prontos. 
            # O .wait() lá em cima é destravado instantaneamente.
            jogador.jogada_evento.set() 
            resposta = str(input("Deseja continuar: "))
            if resposta.lower() == "Sim":
               print("Continuando...")
            else:
                break
            
    except KeyboardInterrupt:
        # Captura CTRL+C garantindo que o programa feche sem estourar Tracebacks feios.
        print("\nDesconectado pelo jogador.")

if __name__ == "__main__":
    main()