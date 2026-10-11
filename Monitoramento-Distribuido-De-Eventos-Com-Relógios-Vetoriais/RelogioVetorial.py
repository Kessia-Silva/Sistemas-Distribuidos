
class RelogioVetorial:
    def __init__(self, processos, processo_atual):
        self.processos = list(processos)
        self.processo_atual = processo_atual

        # Cada processo começa com todas as posições zeradas.
        self.relogio = {
            processo: 0
            for processo in self.processos
        }

    def evento_local(self):
        # Incrementa a posição do processo atual.
        self.relogio[self.processo_atual] += 1

        return self.obter_copia()

    def receber_mensagem(self, relogio_recebido):
        # Combina o relógio local com o relógio recebido,
        # escolhendo o maior valor em cada posição.
        for processo in self.processos:
            self.relogio[processo] = max(
                self.relogio[processo],
                relogio_recebido[processo]
            )

        # O recebimento também é um evento.
        self.relogio[self.processo_atual] += 1

        return self.obter_copia()

    def obter_copia(self):
        # Impede que alterações posteriores no relógio
        # modifiquem o vetor já associado a um evento.
        return self.relogio.copy()

    def __str__(self):
        valores = [
            str(self.relogio[processo])
            for processo in self.processos
        ]

        return "[" + ", ".join(valores) + "]"
