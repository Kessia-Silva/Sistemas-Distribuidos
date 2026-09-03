import socket  # Importa o módulo socket, necessário para comunicação de rede

def main():
    server_port = 8000  # Porta onde o servidor irá escutar por mensagens

    # Cria um socket UDP
    # AF_INET → IPv4
    # SOCK_DGRAM → Protocolo UDP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Associa (bind) o socket a todos os IPs da máquina local e à porta escolhida
    # "0.0.0.0" significa que o servidor aceitará conexões de qualquer IP
    server_socket.bind(("0.0.0.0", server_port))
    
    print("Servidor ativo e aguardando pedidos...")

    while True:
        # Espera por uma mensagem de um cliente (até 40 bytes)
        # recvfrom retorna a mensagem e o endereço do cliente (IP e porta)
        data, client_address = server_socket.recvfrom(40)

        # Converte os bytes recebidos para string
        mensagem = data.decode()
        print(f"Recebido: {mensagem}")

        # Monta a resposta ao cliente
        resposta = f"Resposta ao {mensagem}"

        # Envia a resposta ao cliente
        # resposta.encode() → transforma a string em bytes
        # client_address → tupla (IP, porta) do cliente que enviou a mensagem
        server_socket.sendto(resposta.encode(), client_address)

if __name__ == "__main__":
    main()
