import pickle
import socket
import threading


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("localhost", 5000))
servidor.listen()

#lista que vai armazenar os trabalhadores conectados
trabalhadores = []

# Lista que armazenará as threads criadas.
threads = []

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

# Função responsável por enviar as tarefas para 
# um determinado trabalhador
# conexão -> coneão com o trabalhador
# tarefas -> posições da matriz que ele deverá calcular
def enviarTarefa(conexao, tarefas):
    # Pecorre todas as tarefas atribuídas ao trabalhador
    for l, c in tarefas:
        # Pega a linha da matriz1 e a coluna da matriz2 para calcular a posição [l][c]
        linha, coluna = retornaLinhaColuna(l, c)

        # Converte a l e c para bytes usando pickle
        mensagem = pickle.dumps((linha, coluna))
        #Envia a tarefa para o trabalhador 
        conexao.send(mensagem)

        mensagem = conexao.recv(1024).decode()

        # Converte o resultado recebido de texto para inteiro.
        resultado = int(mensagem)

        # Coloca o resultado na posição correspondente da matriz
        matrizResultado[l][c] = resultado


# Espera os 3 trabalhadores se conectarem
for i in range(3):

    conexao, endereco = servidor.accept()

    trabalhadores.append((conexao, endereco))




# Cria uma thread para cada trabalhador
for i, (conexao, endereco) in enumerate(trabalhadores):

    # Lista de tarefas que serão enviadas
    # para o trabalhador atual.
    tarefas = []

    for l in range(3):
        for c in range(3):


            # Distribui as 9 posições entre os 3 trabalhadores.
            # (l * 3 + c) transforma a posição da matriz
            # em uma sequência de 0 até 8.
            # O resto da divisão por 3 determina
            # qual trabalhador ficará responsável.

            if (l * 3 + c) % 3 == i:
                tarefas.append((l, c))

    # Cria uma thread para o trabalhador atual.
    thread = threading.Thread(
        target=enviarTarefa,
        args=(conexao, tarefas)
    )

    # Guarda a thread na lista
    threads.append(thread)

    # Inicia a execução da thread.
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