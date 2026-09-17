# Implementação via sockets TCP
# Recebe a tarefa (linha e coluna para calculo)

import pickle
import socket

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect(("localhost", 5000))

while True:

    # Recebe a linha e a coluna
    mensagem = cliente.recv(1024)

    if not mensagem:
        break

    linha, coluna = pickle.loads(mensagem)

    # Lógica para multiplicação de matriz
    resultado = 0

    for i in range(len(linha)):
        resultado += linha[i] * coluna[i]

    # Resposta do trabalhador
    cliente.send(str(resultado).encode())

cliente.close()