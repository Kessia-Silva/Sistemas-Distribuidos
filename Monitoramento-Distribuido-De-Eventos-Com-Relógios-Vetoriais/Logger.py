
import os
import threading


class Logger:
    def __init__(self, nome_processo):
        self.nome_processo = nome_processo
        self.lock = threading.Lock()

        # Cria a pasta de logs caso ela ainda não exista.
        os.makedirs("logs", exist_ok=True)

        self.caminho = os.path.join(
            "logs",
            f"{nome_processo}.log"
        )

    def registrar(self, evento):
        mensagem = evento.formatar()

        # Evita que duas threads misturem seus registros.
        with self.lock:
            print(mensagem, flush=True)

            with open(
                self.caminho,
                "a",
                encoding="utf-8"
            ) as arquivo:
                arquivo.write(mensagem + "\n")
