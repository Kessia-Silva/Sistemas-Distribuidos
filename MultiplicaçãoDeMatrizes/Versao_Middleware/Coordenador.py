import Pyro5.api

# Primeira matriz que será multiplicada.
matriz1 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

# Segunda matriz que será multiplicada.
matriz2 = [
    [9, 8, 7],
    [6, 5, 4],
    [3, 2, 1]
]

# Matriz que armazenará os resultados.
matrizResultado = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]

# Cria um Proxy para cada trabalhador.
# PYRONAME:trabalhador1 significa que o Pyro5
# vai procurar no Name Server um objeto registrado
# com esse nome.
trabalhador1 = Pyro5.api.Proxy("PYRONAME:trabalhador1")
trabalhador2 = Pyro5.api.Proxy("PYRONAME:trabalhador2")
trabalhador3 = Pyro5.api.Proxy("PYRONAME:trabalhador3")

# Coloca os três trabalhadores em uma lista.
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

        # Escolhe qual trabalhador realizará o cálculo.
        # (l * 3 + c) transforma a posição da matriz
        # em uma sequência de 0 até 8.
        # O % 3 distribui as tarefas entre os
        # três trabalhadores.
        trabalhador = trabalhadores[(l * 3 + c) % 3]

        # Chama remotamente o método calcular().
        resultado = trabalhador.calcular(linha, coluna)

        #Guarda resultado
        matrizResultado[l][c] = resultado


for linha in matrizResultado:
    print(linha)

# Libera as conexões com os trabalhadores.
trabalhador1._pyroRelease()
trabalhador2._pyroRelease()
trabalhador3._pyroRelease()