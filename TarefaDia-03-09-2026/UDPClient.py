import socket  # Módulo para comunicação de rede
import time    # Módulo para usar a função sleep (pausa)

def main():
    server_address = "127.0.0.1"  # Endereço IP do servidor (localhost)
    server_port = 8000            # Porta usada pelo servidor

    # Cria um socket UDP
    # AF_INET → protocolo IP versão 4 (IPv4)
    # SOCK_DGRAM → usa UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        for i in range(1, 11):  # Envia 10 mensagens para o servidor
            # Cria a mensagem de texto
            mensagem = f"Pedido de Servico {i}"

            # Envia a mensagem codificada em bytes para o servidor
            # .sendto() recebe dois parâmetros:
            #   1. mensagem codificada (em bytes)
            #   2. tupla com (IP do servidor, porta)
            client_socket.sendto(mensagem.encode(), (server_address, server_port))

            # Aguarda a resposta do servidor (até 40 bytes)
            # recvfrom retorna a mensagem e o endereço do servidor
            resposta, _ = client_socket.recvfrom(40)

            # Exibe a resposta, decodificando de bytes para string
            print("Recebida:", resposta.decode())

            # Aguarda 2 segundos antes de enviar a próxima mensagem
            time.sleep(2)

    except Exception as e:
        # Em caso de erro, mostra a mensagem correspondente
        print("Erro:", e)

    finally:
        # Fecha o socket e encerra a comunicação
        client_socket.close()

if __name__ == "__main__":
    main()
