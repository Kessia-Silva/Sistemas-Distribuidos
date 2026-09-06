# Késsia e Ana Paula
# Protocolo escolhido TCP
import socket
import time
# Função principal do cliente
#Jogo da Calculadora - usuário - servidor em que o 
#servidor vai mandar uma operação e o cliente irá responder
def start_client():
    server_address = '127.0.0.1'
    server_port = 8000

    # Criação do socket TCP e conexão com o servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_address, server_port))
        print("[INFO] Conectado ao servidor.")

        # Servidor envia o titulo
        data = client_socket.recv(40).decode()
        print(f"{data}")

        while True:
            # Servidor envia a operação
            data = client_socket.recv(40).decode()
            print(f"Resolva: {data}")

            # Usuario digita a resposta
            resposta = input("Resposta: ")
            client_socket.send(resposta.encode())      

            # Aguarda a resposta do servidor
            resultado = client_socket.recv(40).decode()
            print(f"Recebido: {resultado}")

            sair = input("Quer sair? digite 'sim': ")

            if sair.lower() == "sim":
              break

            # Espera 2 segundos antes de enviar o próximo pedido
            time.sleep(2)

# Início da execução
if __name__ == "__main__":
    start_client()



  




