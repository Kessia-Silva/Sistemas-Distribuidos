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

    # Desempacota os dados recebidos.
    linha, coluna = pickle.loads(mensagem)

   # Variavel que armazenará o resultado
    resultado = 0

    # Percorre os elementos da linha e da coluna.
    # E soma todos os resultados.
    for i in range(len(linha)):
        resultado += linha[i] * coluna[i]

    # envia de volta para o servidor.
    cliente.send(str(resultado).encode())

cliente.close()