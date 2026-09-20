import Pyro5.api


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


trabalhador1 = Pyro5.api.Proxy("PYRONAME:trabalhador1")
trabalhador2 = Pyro5.api.Proxy("PYRONAME:trabalhador2")
trabalhador3 = Pyro5.api.Proxy("PYRONAME:trabalhador3")


trabalhadores = [
    trabalhador1,
    trabalhador2,
    trabalhador3
]


for l in range(3):

    for c in range(3):

        linha = []
        coluna = []

        for j in range(3):
            linha.append(matriz1[l][j])

        for i in range(3):
            coluna.append(matriz2[i][c])

        trabalhador = trabalhadores[(l * 3 + c) % 3]

        resultado = trabalhador.calcular(linha, coluna)

        matrizResultado[l][c] = resultado


for linha in matrizResultado:
    print(linha)


trabalhador1._pyroRelease()
trabalhador2._pyroRelease()
trabalhador3._pyroRelease()