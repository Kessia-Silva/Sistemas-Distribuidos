"""
Created on Wed Sep  9 14:45:37 2026
@author: massa
"""
import Pyro5.api
import threading

# ==========================================
# 1. ABSTRAÇÃO: LÓGICA DE ESTADO DO JOGO
# ==========================================
# Esta classe encapsula as regras de negócio. Ao isolar o tabuleiro,
# garantimos que a lógica da rede não interfira nas regras do jogo (Alta Coesão).
class Tabuleiro:
    def __init__(self):
        # Matriz 3x3 representando o estado inicial do jogo vazio
        self.tabuleiro = [[" " for _ in range(3)] for _ in range(3)]

    def exibir(self):
        # Transforma a matriz em uma representação visual em string para o terminal
        return "\n".join([" | ".join(linha) for linha in self.tabuleiro])

    def jogar(self, linha, coluna, simbolo):
        # Validação de limites (segurança contra entradas maliciosas ou incorretas)
        if 0 <= linha <= 2 and 0 <= coluna <= 2:
            # Garante que a posição não foi sobrescrita
            if self.tabuleiro[linha][coluna] == " ":
                self.tabuleiro[linha][coluna] = simbolo
                return True
        return False

    def verificar_vencedor(self):
        # RECONHECIMENTO DE PADRÕES:
        # Agrupamos todas as combinações possíveis de vitória para analisá-las de forma uniforme.
        # Isso evita dezenas de "if/else" repetitivos.
        linhas = self.tabuleiro
        colunas = list(zip(*self.tabuleiro)) # Transposição da matriz (lê colunas como linhas)
        diagonais = [
            [self.tabuleiro[i][i] for i in range(3)],
            [self.tabuleiro[i][2 - i] for i in range(3)]
        ]

        # Itera sobre todas as trilhas possíveis buscando uma onde os 3 elementos são iguais e não vazios
        for trio in linhas + colunas + diagonais:
            if trio[0] != " " and trio.count(trio[0]) == 3:
                return trio[0] # Retorna "X" ou "O"
        return None

    def completo(self):
        # Verifica se ainda há espaços em branco. Útil para declarar empate (Deu Velha).
        return all(cell != " " for row in self.tabuleiro for cell in row)


# ==========================================
# 2. DECOMPOSIÇÃO: GERENCIAMENTO DE REDE
# ==========================================
# O decorador @expose diz ao middleware do Pyro que os métodos públicos desta 
# classe estão liberados para serem acessados remotamente pelos clientes.
@Pyro5.api.expose
class ServidorJogo:
    def __init__(self):
        # O __init__ agora será executado UMA ÚNICA VEZ (Padrão Singleton implementado na main).
        self.fila = []
        # Mutex (Lock) necessário para evitar condições de corrida (Race Conditions)
        # caso dezenas de clientes tentem se conectar no exato mesmo milissegundo.
        self.lock = threading.Lock()
        print("[SISTEMA] Estrutura de dados do servidor iniciada.")

    def iniciar_jogo(self, jogador_uri):
        # ==========================================
        # CONCORRÊNCIA DO PYRO5 (Ownership):
        # Não instanciamos o Proxy() aqui na thread principal. 
        # O Pyro amarra o Proxy à thread que o criou. Se criarmos aqui, 
        # a thread da partida (que roda em background) não terá permissão para usá-lo.
        # Por isso, guardamos apenas a STRING (URI) na fila.
        # ==========================================
        
        print(f"[REDE] Novo jogador conectado. URI: {jogador_uri}")
        
        # Seção Crítica: O Lock garante que apenas uma thread altere a fila por vez
        with self.lock:
            self.fila.append(jogador_uri)
            
            # Algoritmo de emparelhamento: a cada 2 jogadores, retira da fila e inicia a partida
            if len(self.fila) >= 2:
                uri1 = self.fila.pop(0)
                uri2 = self.fila.pop(0)
                print("[SISTEMA] 2 jogadores encontrados. Iniciando partida em nova thread...")
                
                # A partida roda em uma nova Thread, recebendo as URIs (Strings).
                # daemon=True assegura que se o servidor cair, as threads filhas morrem.
                threading.Thread(target=self._partida, args=(uri1, uri2), daemon=True).start()


    # ==========================================
    # 3. MÁQUINA DE ESTADOS DA PARTIDA
    # ==========================================
    def _partida(self, uri1, uri2):
        # ==========================================
        # CONCORRÊNCIA DO PYRO5 (Ownership):
        # Os proxies são instanciados AQUI, dentro da thread que vai 
        # efetivamente usá-los para se comunicar com os clientes via RPC.
        # ==========================================
        j1 = Pyro5.api.Proxy(uri1)
        j2 = Pyro5.api.Proxy(uri2)

        j1.receber_mensagem("Digite seu nome:")
        j2.receber_mensagem("Digite seu nome:")

        nome1 = j1.responder()
        nome2 = j2.responder()

        print(f"[SISTEMA] Jogadores: {nome1} e {nome2}")
        
        tab = Tabuleiro()
        # Mapeamento estático dos papéis de cada jogador
        jogadores = [(j1, "X",nome1), (j2, "O",nome2)]

        try:
            # Envia a mensagem de boas-vindas
            for jogador, simbolo,nome in jogadores:
                jogador.receber_mensagem(f"\n--- A partida vai começar {nome}! Você joga com '{simbolo}' ---")

            atual = 0 # Índice que alterna entre 0 e 1 para gerenciar o turno
            
            # Loop principal do jogo
            while True:
                jogador, simbolo, nome = jogadores[atual]
                outro_jogador, outro_simbolo, outro_nome = jogadores[1 - atual]

                # Atualiza a interface (CLI) de ambos os jogadores
                jogador.receber_mensagem("\n" + tab.exibir())
                outro_jogador.receber_mensagem("\n" + tab.exibir())
                outro_jogador.receber_mensagem(f"{outro_nome} aguarde o turno do seu adversário {nome}...")

                # --- PONTO DE SINCRONIZAÇÃO (RPC Bloqueante) ---
                # A thread desta partida no servidor fica pausada (bloqueada) 
                # aguardando o retorno da tupla (linha, coluna) pelo cliente pela rede.
                linha, coluna = jogador.fazer_jogada()

                # Processa o lance usando a classe abstrata de regras
                if tab.jogar(linha, coluna, simbolo):
                    vencedor = tab.verificar_vencedor()
                    
                    if vencedor:
                        msg = f"\n{tab.exibir()}\nFim de Jogo! Jogador '{vencedor}' venceu!"
                        j1.receber_mensagem(msg)
                        j2.receber_mensagem(msg)
                        j1.finalizar() # Sinaliza ao cliente que ele pode encerrar seu terminal
                        j2.finalizar()

                        msg2 = f"\n{tab.exibir()}\nDeseja uma revanche? "
                        j1.receber_mensagem(msg2)
                        j2.receber_mensagem(msg2)

                        

                        
                         # Pergunta se quer continuar com o jogo
                    elif tab.completo():
                        msg = f"\n{tab.exibir()}\nFim de Jogo! Empate!"
                        j1.receber_mensagem(msg)
                        j2.receber_mensagem(msg)
                        j1.finalizar()
                        j2.finalizar()
                        msg3 = f"\n{tab.exibir()}\nDeseja uma revanche? "

                        break
                        
                    # Alterna o turno matematicamente (0 vira 1, 1 vira 0)
                    atual = 1 - atual
                else:
                    # Se a jogada falhar (posição ocupada), o turno NÃO alterna.
                    # O mesmo jogador será cobrado novamente no próximo ciclo do while.
                    jogador.receber_mensagem("Jogada inválida! A posição pode estar ocupada ou fora dos limites.")
                    
        except Exception as e:
            # Tratamento de resiliência: se um cliente fechar o terminal abruptamente (Broken Pipe),
            # capturamos o erro na rede e avisamos o jogador restante antes de matar a thread.
            print(f"[ERRO] Partida interrompida (Erro ou Desconexão): {e}")
            try: j1.finalizar() 
            except: pass
            try: j2.finalizar()
            except: pass

def main():
    # Inicialização do middleware RPC
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    
    # ==========================================
    # ARQUITETURA: PADRÃO SINGLETON (Instância Única)
    # ==========================================
    # 1. Instanciamos o objeto AQUI. O __init__() é executado neste exato momento,
    # criando a self.fila que será compartilhada (em memória) por todos os clientes.
    instancia_servidor = ServidorJogo()
    
    # 2. Registramos a INSTÂNCIA já criada no Pyro.
    # O Pyro usará este mesmo objeto para todas as chamadas.
    uri = daemon.register(instancia_servidor)
    
    # Registra a URI no Servidor de Nomes global para os clientes localizarem
    ns.register("jogodavelha.servidor", uri)
    
    print("[SISTEMA] Servidor de Jogo da Velha registrado no Name Server e aguardando jogadores...")
    
    # Inicia o loop de escuta (A thread principal fica bloqueada aqui mantendo o servidor vivo)
    daemon.requestLoop()

if __name__ == "__main__":
    main()