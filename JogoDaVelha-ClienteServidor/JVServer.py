# Alunas Ana Paula e Késsia


import Pyro5.api
import threading
import time

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

        colunas = list(zip(*self.tabuleiro))  # Transposição da matriz (lê colunas como linhas)

        diagonais = [
            [self.tabuleiro[i][i] for i in range(3)],
            [self.tabuleiro[i][2 - i] for i in range(3)]
        ]

        # Itera sobre todas as trilhas possíveis buscando uma onde os 3 elementos são iguais e não vazios
        for trio in linhas + colunas + diagonais:

            if trio[0] != " " and trio.count(trio[0]) == 3:
                return trio[0]  # Retorna "X" ou "O"

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

        # Controle de sincronização da revanche.
        # Guarda a resposta de cada jogador até que os dois tenham respondido.
        self.respostas_revanche = {}

        # Evento usado para bloquear a thread da partida
        # até que os dois jogadores respondam à revanche.
        self.revanche_evento = threading.Event()

        # Lock exclusivo para proteger as respostas da revanche
        # contra acessos simultâneos das threads do Pyro.
        self.lock_revanche = threading.Lock()

        # ==========================================
        # CONTROLE DE CONEXÃO DOS JOGADORES
        # ==========================================
        # Guarda o horário do último heartbeat recebido de cada jogador.
        self.ultimos_heartbeats = {}

        # Lock exclusivo para proteger o dicionário de heartbeats.
        self.lock_heartbeat = threading.Lock()

        # Guarda qual é o oponente de cada jogador que está em uma partida.
        self.partidas = {}

        # Lock exclusivo para proteger o controle das partidas.
        self.lock_partidas = threading.Lock()

        # Inicia a thread responsável por verificar jogadores desconectados.
        threading.Thread(
            target=self._monitorar_conexoes,
            daemon=True
        ).start()

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

        # Registra o momento em que o jogador entrou no servidor.
        with self.lock_heartbeat:
            self.ultimos_heartbeats[jogador_uri] = time.time()

        # Seção Crítica: O Lock garante que apenas uma thread altere a fila por vez
        with self.lock:

            self.fila.append(jogador_uri)

            # Algoritmo de emparelhamento: a cada 2 jogadores,
            # retira da fila e inicia a partida.
            if len(self.fila) >= 2:

                uri1 = self.fila.pop(0)
                uri2 = self.fila.pop(0)

                # Registra os dois jogadores como participantes da mesma partida.
                with self.lock_partidas:
                    self.partidas[uri1] = uri2
                    self.partidas[uri2] = uri1

                print(
                    "[SISTEMA] 2 jogadores encontrados. "
                    "Iniciando partida em nova thread..."
                )

                # A partida roda em uma nova Thread, recebendo as URIs (Strings).
                # daemon=True assegura que se o servidor cair, as threads filhas morrem.

                threading.Thread(
                    target=self._partida,
                    args=(uri1, uri2),
                    daemon=True
                ).start()

    # ==========================================
    # 3. DECOMPOSIÇÃO: SINCRONIZAÇÃO DA REVANCHE
    # ==========================================

    def responder_revanche(self, jogador_uri, resposta):

        # Lock garante que dois jogadores não alterem
        # o dicionário de respostas ao mesmo tempo.
        with self.lock_revanche:

            # Armazena a resposta do jogador usando sua URI como identificação.
            self.respostas_revanche[jogador_uri] = resposta.lower()

            print(
                f"[SISTEMA] Resposta de revanche recebida: "
                f"{resposta.lower()}"
            )

            # Verifica se os dois jogadores já responderam.
            if len(self.respostas_revanche) >= 2:

                # Acorda a thread da partida, que estava esperando
                # a resposta do segundo jogador.
                self.revanche_evento.set()

    # ==========================================
    # 4. DECOMPOSIÇÃO: PLACAR
    # ==========================================

    def exibir_placar(self, nome1, nome2, placar):

        return (
            f"Placar: {nome1} {placar[nome1]} x "
            f"{placar[nome2]} {nome2}"
        )

    # ==========================================
    # 5. CONTROLE DE CONEXÃO
    # ==========================================

    def heartbeat(self, jogador_uri):

        # Atualiza o horário do último sinal recebido do jogador.
        with self.lock_heartbeat:
            self.ultimos_heartbeats[jogador_uri] = time.time()

    def desconectar(self, jogador_uri):

        # Método chamado pelo cliente quando o jogador encerra
        # voluntariamente o programa usando CTRL+C.
        print(
            f"[REDE] Jogador desconectou voluntariamente. "
            f"URI: {jogador_uri}"
        )

        self._tratar_desconexao(jogador_uri)

    def _monitorar_conexoes(self):

        # Tempo máximo sem receber heartbeat antes de considerar
        # que o jogador perdeu a conexão.
        TIMEOUT = 60

        while True:

            # Verifica as conexões periodicamente.
            time.sleep(5)

            agora = time.time()
            desconectados = []

            with self.lock_heartbeat:

                for jogador_uri, ultimo_heartbeat in list(
                    self.ultimos_heartbeats.items()
                ):

                    if agora - ultimo_heartbeat > TIMEOUT:
                        desconectados.append(jogador_uri)

            # Trata os jogadores fora do Lock para não bloquear
            # o recebimento de novos heartbeats.
            for jogador_uri in desconectados:

                print(
                    f"[REDE] Timeout detectado para o jogador: "
                    f"{jogador_uri}"
                )

                self._tratar_desconexao(jogador_uri)

    def _tratar_desconexao(self, jogador_uri):

        oponente_uri = None

        # ==========================================
        # REMOVE O JOGADOR DA FILA
        # ==========================================

        with self.lock:

            if jogador_uri in self.fila:
                self.fila.remove(jogador_uri)

        # ==========================================
        # LOCALIZA A PARTIDA DO JOGADOR
        # ==========================================

        with self.lock_partidas:

            oponente_uri = self.partidas.get(jogador_uri)

            if oponente_uri is not None:

                # Remove os dois jogadores da estrutura da partida.
                self.partidas.pop(jogador_uri, None)
                self.partidas.pop(oponente_uri, None)

        # ==========================================
        # REMOVE O HEARTBEAT
        # ==========================================

        with self.lock_heartbeat:

            self.ultimos_heartbeats.pop(jogador_uri, None)

        # ==========================================
        # LIMPA RESPOSTAS DE REVANCHE
        # ==========================================

        with self.lock_revanche:

            self.respostas_revanche.pop(jogador_uri, None)

            # Se a thread da partida estiver esperando
            # uma resposta de revanche, acordamos a thread.
            self.revanche_evento.set()

        # ==========================================
        # AVISA O OPONENTE
        # ==========================================

        if oponente_uri is not None:

            try:

                oponente = Pyro5.api.Proxy(oponente_uri)

                oponente.receber_mensagem(
                    "\nOponente desconectado. "
                    "Você venceu por W.O."
                )

                oponente.finalizar()

            except Exception as e:

                print(
                    f"[ERRO] Não foi possível avisar o oponente: {e}"
                )

            print(
                "[SISTEMA] Partida removida da memória do servidor "
                "após desconexão."
            )

    # ==========================================
    # 6. MÁQUINA DE ESTADOS DA PARTIDA
    # ==========================================

    def _partida(self, uri1, uri2):

        # ==========================================
        # CONCORRÊNCIA DO PYRO5 (Ownership):
        # Os proxies são instanciados AQUI, dentro da thread que vai
        # efetivamente usá-los para se comunicar com os clientes via RPC.
        # ==========================================

        j1 = Pyro5.api.Proxy(uri1)
        j2 = Pyro5.api.Proxy(uri2)

        nome1 = j1.responder()
        nome2 = j2.responder()

        print(f"[SISTEMA] Jogadores: {nome1} e {nome2}")

        # Mapeamento estático dos papéis de cada jogador.
        # O jogador 1 continua sendo X e o jogador 2 continua sendo O
        # durante todas as revanches.
        jogadores = [
            (j1, "X", nome1),
            (j2, "O", nome2)
        ]

        # ==========================================
        # PLACAR CONTÍNUO
        # ==========================================
        # O placar é criado UMA ÚNICA VEZ para esta disputa.
        #
        # Diferentemente do tabuleiro, ele NÃO será recriado
        # quando uma revanche começar.

        placar = {
            nome1: 0,
            nome2: 0
        }

        try:

            # Envia a mensagem de boas-vindas
            for jogador, simbolo, nome in jogadores:

                jogador.receber_mensagem(
                    f"\n--- A partida vai começar {nome}! "
                    f"Você joga com '{simbolo}' ---"
                )

            # Índice que alterna entre 0 e 1 para gerenciar o turno
            atual = 0

            # ==========================================
            # LOOP CONTÍNUO DAS PARTIDAS
            # ==========================================
            #
            # Cada "continue" abaixo começa uma nova partida
            # na MESMA thread _partida.
            #
            # Apenas o objeto Tabuleiro é recriado.
            # O placar permanece.

            while True:

                # ==========================================
                # NOVO TABULEIRO
                # ==========================================
                # Aqui o tabuleiro é zerado para uma nova partida.
                #
                # O placar NÃO é zerado.

                tab = Tabuleiro()

                print(
                    f"[SISTEMA] Nova partida iniciada. "
                    f"{self.exibir_placar(nome1, nome2, placar)}"
                )

                # O jogador X começa todas as novas partidas.
                atual = 0

                # ==========================================
                # LOOP PRINCIPAL DO JOGO ATUAL
                # ==========================================

                while True:

                    jogador, simbolo, nome = jogadores[atual]
                    outro_jogador, outro_simbolo, outro_nome = jogadores[1 - atual]

                    # Atualiza a interface (CLI) de ambos os jogadores
                    jogador.receber_mensagem("\n" + tab.exibir())

                    outro_jogador.receber_mensagem("\n" + tab.exibir())

                    outro_jogador.receber_mensagem(
                        f"{outro_nome} aguarde o turno do seu adversário {nome}..."
                    )

                    # ==========================================
                    # PONTO DE SINCRONIZAÇÃO (RPC Bloqueante)
                    # ==========================================
                    # A thread desta partida no servidor fica pausada
                    # aguardando o retorno da tupla (linha, coluna)
                    # pelo cliente pela rede.

                    linha, coluna = jogador.fazer_jogada()

                    # Processa o lance usando a classe abstrata de regras
                    if tab.jogar(linha, coluna, simbolo):

                        vencedor = tab.verificar_vencedor()

                        # ==========================================
                        # VITÓRIA
                        # ==========================================

                        if vencedor:

                            # Descobre qual nome corresponde ao símbolo vencedor.
                            if vencedor == "X":
                                nome_vencedor = nome1
                            else:
                                nome_vencedor = nome2

                            # Atualiza o placar ANTES de perguntar
                            # se os jogadores querem revanche.
                            placar[nome_vencedor] += 1

                            # Monta a mensagem com o novo placar.
                            msg = (
                                f"\n{tab.exibir()}"
                                f"\nFim de Jogo! Jogador '{nome_vencedor}' venceu!"
                                f"\n{self.exibir_placar(nome1, nome2, placar)}"
                            )

                            j1.receber_mensagem(msg)
                            j2.receber_mensagem(msg)

                            # Avisa aos clientes que a partida terminou.
                            # Isso permite que a Main Thread do cliente
                            # acorde e faça a pergunta sobre a revanche.

                            j1.partida_terminou()
                            j2.partida_terminou()

                            # ==========================================
                            # SINCRONIZAÇÃO DA REVANCHE
                            # ==========================================

                            # Limpa as respostas anteriores antes de iniciar
                            # uma nova rodada de decisão.

                            with self.lock_revanche:
                                self.respostas_revanche.clear()
                                self.revanche_evento.clear()

                            # A thread da partida fica bloqueada aqui.
                            # Ela só continuará quando os DOIS jogadores
                            # responderem à pergunta da revanche.

                            self.revanche_evento.wait()

                            # Depois que os dois responderam,
                            # verifica as respostas.

                            with self.lock_revanche:

                                resposta1 = self.respostas_revanche.get(
                                    uri1,
                                    "nao"
                                )

                                resposta2 = self.respostas_revanche.get(
                                    uri2,
                                    "nao"
                                )

                                if (
                                    resposta1 == "sim"
                                    and resposta2 == "sim"
                                ):

                                    # Os dois jogadores aceitaram a revanche.
                                    #
                                    # NÃO criamos uma nova thread.
                                    # O "continue" volta para o while True
                                    # das partidas dentro desta mesma _partida.

                                    self.respostas_revanche.clear()
                                    self.revanche_evento.clear()

                                    print(
                                        "[SISTEMA] Ambos aceitaram a revanche. "
                                        "Iniciando nova partida na mesma thread."
                                    )

                                    continue

                                else:

                                    # Pelo menos um jogador recusou a revanche.

                                    self.respostas_revanche.clear()
                                    self.revanche_evento.clear()

                                    print(
                                        "[SISTEMA] Revanche recusada. "
                                        "Encerrando partida."
                                    )

                                    # Sinaliza aos clientes que eles podem
                                    # encerrar seus terminais.

                                    j1.finalizar()
                                    j2.finalizar()

                                    # Remove a partida da memória do servidor.
                                    with self.lock_partidas:
                                        self.partidas.pop(uri1, None)
                                        self.partidas.pop(uri2, None)

                                    # Remove os heartbeats dos jogadores.
                                    with self.lock_heartbeat:
                                        self.ultimos_heartbeats.pop(uri1, None)
                                        self.ultimos_heartbeats.pop(uri2, None)

                                    break

                        # ==========================================
                        # EMPATE
                        # ==========================================

                        elif tab.completo():

                            msg = (
                                f"\n{tab.exibir()}"
                                f"\nFim de Jogo! Empate!"
                                f"\n{self.exibir_placar(nome1, nome2, placar)}"
                            )

                            j1.receber_mensagem(msg)
                            j2.receber_mensagem(msg)

                            # Avisa aos clientes que a partida terminou.
                            j1.partida_terminou()
                            j2.partida_terminou()

                            # ==========================================
                            # SINCRONIZAÇÃO DA REVANCHE
                            # ==========================================

                            # Limpa as respostas anteriores antes de iniciar
                            # uma nova rodada de decisão.

                            with self.lock_revanche:
                                self.respostas_revanche.clear()
                                self.revanche_evento.clear()

                            # A thread da partida fica bloqueada aqui.
                            # Ela só continuará quando os DOIS jogadores
                            # responderem à revanche.

                            self.revanche_evento.wait()

                            # Depois que os dois responderam,
                            # verifica as respostas.

                            with self.lock_revanche:

                                resposta1 = self.respostas_revanche.get(
                                    uri1,
                                    "nao"
                                )

                                resposta2 = self.respostas_revanche.get(
                                    uri2,
                                    "nao"
                                )

                                if (
                                    resposta1 == "sim"
                                    and resposta2 == "sim"
                                ):

                                    # Os dois jogadores aceitaram a revanche.
                                    #
                                    # O placar permanece o mesmo porque
                                    # houve empate.
                                    #
                                    # Apenas o tabuleiro será recriado.

                                    self.respostas_revanche.clear()
                                    self.revanche_evento.clear()

                                    print(
                                        "[SISTEMA] Ambos aceitaram a revanche. "
                                        "Iniciando nova partida na mesma thread."
                                    )

                                    continue

                                else:

                                    # Pelo menos um jogador recusou a revanche.

                                    self.respostas_revanche.clear()
                                    self.revanche_evento.clear()

                                    print(
                                        "[SISTEMA] Revanche recusada. "
                                        "Encerrando partida."
                                    )

                                    j1.finalizar()
                                    j2.finalizar()

                                    # Remove a partida da memória do servidor.
                                    with self.lock_partidas:
                                        self.partidas.pop(uri1, None)
                                        self.partidas.pop(uri2, None)

                                    # Remove os heartbeats dos jogadores.
                                    with self.lock_heartbeat:
                                        self.ultimos_heartbeats.pop(uri1, None)
                                        self.ultimos_heartbeats.pop(uri2, None)

                                    break

                        # ==========================================
                        # PRÓXIMO TURNO
                        # ==========================================

                        # Alterna o turno matematicamente
                        # (0 vira 1, 1 vira 0).

                        atual = 1 - atual

                    else:

                        # Se a jogada falhar (posição ocupada), o turno NÃO alterna.
                        # O mesmo jogador será cobrado novamente no próximo ciclo do while.

                        jogador.receber_mensagem(
                            "Jogada inválida! A posição pode estar ocupada "
                            "ou fora dos limites."
                        )

        except Exception as e:

            # Tratamento de resiliência: se um cliente fechar o terminal
            # abruptamente (Broken Pipe), capturamos o erro na rede e
            # avisamos o jogador restante antes de matar a thread.

            print(
                f"[ERRO] Partida interrompida "
                f"(Erro ou Desconexão): {e}"
            )

            # Limpa a partida da memória do servidor.
            with self.lock_partidas:
                self.partidas.pop(uri1, None)
                self.partidas.pop(uri2, None)

            # Remove os heartbeats dos jogadores.
            with self.lock_heartbeat:
                self.ultimos_heartbeats.pop(uri1, None)
                self.ultimos_heartbeats.pop(uri2, None)

            try:
                j1.finalizar()
            except:
                pass

            try:
                j2.finalizar()
            except:
                pass


def main():

    # Inicialização do middleware RPC
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()

    # ==========================================
    # ARQUITETURA: PADRÃO SINGLETON (Instância Única)
    # ==========================================

    # 1. Instanciamos o objeto AQUI. O __init__ é executado neste exato momento,
    # criando a self.fila que será compartilhada (em memória) por todos os clientes.

    instancia_servidor = ServidorJogo()

    # 2. Registramos a INSTÂNCIA já criada no Pyro.
    # O Pyro usará este mesmo objeto para todas as chamadas.

    uri = daemon.register(instancia_servidor)

    # Registra a URI no Servidor de Nomes global para os clientes localizarem
    ns.register("jogodavelha.servidor", uri)

    print(
        "[SISTEMA] Servidor de Jogo da Velha registrado "
        "no Name Server e aguardando jogadores..."
    )

    # Inicia o loop de escuta
    # (A thread principal fica bloqueada aqui mantendo o servidor vivo)

    daemon.requestLoop()


if __name__ == "__main__":
    main()