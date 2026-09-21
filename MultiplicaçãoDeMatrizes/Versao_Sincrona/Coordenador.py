# Servidor que vai dirigir os processos e distribuir as funções
# definição de configuração do socket
import pickle
import socket



servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("localhost", 5000))

#lista que vai armazenar os trabalhadores conectados
trabalhadores = []

# Primeira matriz que será multiplicada
matriz1 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# Segunda matriz que será multiplicada
matriz2 = [
    [9, 8, 7],
    [6, 5, 4],
    [3, 2, 1]
]

# Matriz onde serão armazenadas os resultados
matrizResultado = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]

servidor.listen()

# Função responsável por pegar uma linha da matriz1 
# e uma coluna da matriz2
def retornaLinhaColuna(l, c):
    linha = []
    coluna = []

    # Percorre a linha l da matriz1
    for j in range(3):
        linha.append(matriz1[l][j])

    # Percorre a coluna c da matriz2
    for i in range(3):
        coluna.append(matriz2[i][c])

    # Retorna a linha e a coluna
    return linha, coluna

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
        resultado = int(mensagem)
        matrizResultado[l][c] = resultado
        i = (i + 1) % 3 # Para saber qual trabalhador está
for linha in matrizResultado:
    print(linha)
# acabou o calculo, encerra tudo
conexao.close()
servidor.close()


