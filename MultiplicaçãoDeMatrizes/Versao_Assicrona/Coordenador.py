import pickle
import socket
import threading


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("localhost", 5000))
servidor.listen()

trabalhadores = []

matriz1 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

matriz2 = [
    [9, 8, 7],
    [6, 5, 4],
    [3, 2, 1]
]

matrizResultado = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]


def retornaLinhaColuna(l, c):

    linha = []
    coluna = []

    for j in range(3):
        linha.append(matriz1[l][j])

    for i in range(3):
        coluna.append(matriz2[i][c])

    return linha, coluna


def enviarTarefa(conexao, tarefas):

    for l, c in tarefas:

        linha, coluna = retornaLinhaColuna(l, c)

        mensagem = pickle.dumps((linha, coluna))
        conexao.send(mensagem)

        mensagem = conexao.recv(1024).decode()

        resultado = int(mensagem)

        matrizResultado[l][c] = resultado


# Espera os 3 trabalhadores se conectarem
for i in range(3):

    conexao, endereco = servidor.accept()

    trabalhadores.append((conexao, endereco))


threads = []


# Cria uma thread para cada trabalhador
for i, (conexao, endereco) in enumerate(trabalhadores):

    tarefas = []

    for l in range(3):
        for c in range(3):

            if (l * 3 + c) % 3 == i:
                tarefas.append((l, c))

    thread = threading.Thread(
        target=enviarTarefa,
        args=(conexao, tarefas)
    )

    threads.append(thread)

    thread.start()


# Espera todas as threads terminarem
for thread in threads:
    thread.join()


# Mostra a matriz resultado
for linha in matrizResultado:
    print(linha)


# Fecha as conexões
for conexao, endereco in trabalhadores:
    conexao.close()

servidor.close()