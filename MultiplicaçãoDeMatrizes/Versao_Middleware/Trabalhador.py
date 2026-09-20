import Pyro5.api


@Pyro5.api.expose
class Trabalhador:

    def calcular(self, linha, coluna):

        resultado = 0

        for i in range(len(linha)):
            resultado += linha[i] * coluna[i]

        return resultado


daemon = Pyro5.api.Daemon()
ns = Pyro5.api.locate_ns()

trabalhador = Trabalhador()

uri = daemon.register(trabalhador)

nome = input("Digite o nome do trabalhador: ")

ns.register(nome, uri)

print(f"{nome} pronto.")

daemon.requestLoop()