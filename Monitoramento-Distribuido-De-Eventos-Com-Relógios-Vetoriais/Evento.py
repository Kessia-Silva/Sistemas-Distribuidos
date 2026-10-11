
from datetime import datetime


class Evento:
    def __init__(
        self,
        processo,
        numero,
        tipo,
        instante,
        relogio,
        origem=None,
        destino=None,
        evento_origem=None
    ):
        self.processo = processo
        self.numero = numero
        self.tipo = tipo
        self.instante = instante
        self.relogio = dict(relogio)
        self.origem = origem
        self.destino = destino
        self.evento_origem = evento_origem

    @staticmethod
    def agora():
        # Horário local com precisão de milissegundos.
        return datetime.now().astimezone().isoformat(
            timespec="milliseconds"
        )

    def formatar(self):
        partes = [
            f"[{self.instante}]",
            f"Processo={self.processo}",
            f"Evento=E{self.numero}",
            f"Tipo={self.tipo}",
            f"Relógio={self.relogio}"
        ]

        if self.origem:
            partes.append(f"Origem={self.origem}")

        if self.destino:
            partes.append(f"Destino={self.destino}")

        if self.evento_origem is not None:
            partes.append(
                f"EventoLocalRelacionado=E{self.evento_origem}"
            )

        return " | ".join(partes)

    def __str__(self):
        return self.formatar()
