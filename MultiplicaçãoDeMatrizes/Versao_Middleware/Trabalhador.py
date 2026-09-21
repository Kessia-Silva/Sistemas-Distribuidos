import Pyro5.api


@Pyro5.api.expose
class Trabalhador:

    # Método que será chamado remotamente
    # pelo coordenador.
    def calcular(self, linha, coluna):

        resultado = 0

        
        for i in range(len(linha)):
            # Faz a multiplicação dos elementos
            # correspondentes e soma ao resultado.
            resultado += linha[i] * coluna[i]

        return resultado


daemon = Pyro5.api.Daemon()
# Localiza o Name Server do Pyro5.
ns = Pyro5.api.locate_ns()
# Cria uma instância da classe Trabalhador.
trabalhador = Trabalhador()
# Registra o trabalhador no Daemon.
uri = daemon.register(trabalhador)

# Pergunta ao usuário qual será o nome
# desse trabalhador.
nome = input("Digite o nome do trabalhador: ")

# Registra o trabalhador no Name Server
# usando o nome informado.
ns.register(nome, uri)

# Mostra uma mensagem indicando que
# o trabalhador está pronto.
print(f"{nome} pronto.")

daemon.requestLoop()