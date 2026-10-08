class RelogioVetorial:

    def __init__(self, processos, processo_atual):

        self.processos = processos

        self.processo_atual = processo_atual

        # Inicialmente todos os processos possuem valor 0 no relógio.
        self.relogio = {
            processo: 0
            for processo in processos
        }

    # Atualiza o relógio quando acontece um evento local.

    def evento_local(self):

        # Incrementa somente a posição correspondente ao processo atual.
        self.relogio[self.processo_atual] += 1

        return self.obter_copia()

    # Atualiza o relógio quando uma mensagem é recebida.

    def receber_mensagem(self, relogio_recebido):
       
        # Percorre todos os processos.
        for processo in self.processos:

            # Escolhe o maior valor entre: relógio local e relógio recebido
            
            self.relogio[processo] = max(
                self.relogio[processo],
                relogio_recebido[processo]
            )

        # O recebimento da mensagem também é considerado um evento.
        self.relogio[self.processo_atual] += 1

        return self.obter_copia()

    # Retorna uma cópia do relógio atual

    def obter_copia(self):

        return self.relogio.copy()


    def __str__(self):

        valores = [
            str(self.relogio[processo])
            for processo in self.processos
        ]

        return "[" + ",".join(valores) + "]"
    
    

