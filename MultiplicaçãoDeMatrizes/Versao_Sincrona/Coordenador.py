# Servidor que vai dirigir os processos e distribuir as funções
# definição de configuração do socket
import pickle
import socket

def retornaLinhaColuna(l, c):
    linha = []
    coluna = []

    for j in range(3):
        linha.append(matriz[l][j])

    for i in range(3):
        coluna.append(matriz[i][c])

    return linha, coluna


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("localhost", 5000))

trabalhadores = []
matriz = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

servidor.listen()

# Espera os trabalhadores se conectarem (trabalhadores 3) - Loop?
for i in range(3):
    # regista os trabalhadores numa lista
    conexao, endereco = servidor.accept()
    trabalhadores.append((conexao, endereco))
i = 0
# Envia a linha e coluna para cada trabalhador
for l in range(3):
    for c in range(3):

        linha, coluna = retornaLinhaColuna(l, c)

        # escolher um trabalhador e envia a linha e coluna
        conexao, endereco = trabalhadores[i]
        mensagem = pickle.dumps((linha, coluna))
        conexao.send(mensagem)
        # Espera o trabalhador enviar o resultado
        mensagem = conexao.recv(1024).decode()
        print(mensagem)
        i = (i + 1) % 3 # Para saber qual trabalhador está

# acabou o calculo, encerra tudo
conexao.close()
servidor.close()


