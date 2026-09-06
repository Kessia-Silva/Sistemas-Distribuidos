# Késsia e Ana Paula
import socket
import threading
import random


# Classe que representa uma thread para lidar com cada cliente
class ClientThread(threading.Thread):
    def __init__(self, client_socket, address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        print(f"[INFO] Conectado a {address}")

    def run(self):
        try:
            # Inicio de jogo - Mensagem
            response = "Bem vindo ao jogo da calculadora"
            self.client_socket.send(response.encode())

            while True:
                # numeros e operações randomizadas
                operacoes = ['+', '-', '*', '/']
                a = random.randint(1, 100)
                b = random.randint(1, 100)
                op = random.choice(operacoes)
                response = f"{a} {op} {b} ="
                #envia operação para o cliente
                self.client_socket.send(response.encode())

                # Recebe a resposta do cliente
                resposta = self.client_socket.recv(40).decode()

                # Calcula o resultado correto
                if op == '+':
                  resultado = a + b

                elif op == '-':
                  resultado = a - b

                elif op == '*':
                  resultado = a * b

                elif op == '/':
                  resultado = round(a / b, 1) #permite uma casa decimal

                if not resposta:
                    break
                # Compara a resposta do usuário com o resultado correto
                if str(resultado).lower()== resposta.lower():
                   print("Resposta correta!")
                   self.client_socket.send("Correto!".encode())
                else:
                   print("Resposta incorreta!")
                   self.client_socket.send(
                   f"Errado! A resposta correta é {resultado}".encode())
                
        except Exception as e:
            print(f"[ERRO] {e}")
        finally:
            self.client_socket.close()
            print(f"[INFO] Conexão com {self.address} encerrada.")

# Função principal do servidor
def start_server():
    server_port = 8000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', server_port))
    server_socket.listen()

    print(f"[INFO] Servidor escutando na porta {server_port}...")

    # Loop principal para aceitar conexões de clientes
    while True:
        client_socket, addr = server_socket.accept()
        thread = ClientThread(client_socket, addr)
        thread.start()

# Início da execução
if __name__ == "__main__":
    start_server()
