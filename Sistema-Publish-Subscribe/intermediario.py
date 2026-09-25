import Pyro5.api


# Tópicos disponíveis no sistema
topicos = []

# Subscribers registrados: ID -> URI do objeto remoto
subscribers = {}

# Relação entre subscribers e tópicos
inscricoes = []


@Pyro5.api.expose
class Intermediario:

    def criar_topico(self, nome):
        if nome not in topicos:
            topicos.append(nome)
            print(f"Tópico criado: {nome}")

    def registrar_subscriber(self, id_subscriber, uri_subscriber):
        print(f"Registrando subscriber: {id_subscriber}")

        # Guarda a URI para realizar o callback remoto
        subscribers[id_subscriber] = uri_subscriber

        # Remove inscrições antigas desse subscriber
        # caso ele esteja se registrando novamente
        inscricoes[:] = [
            inscricao
            for inscricao in inscricoes
            if inscricao["subscriber"] != id_subscriber
        ]

    # Registra o subscriber no tópico desejado
    def inscrever(self, id_subscriber, topico):
        print(f"Inscrevendo {id_subscriber} no tópico {topico}")

        if topico in topicos and id_subscriber in subscribers:

            # Evita inscrições duplicadas
            inscricao_existente = {
                "subscriber": id_subscriber,
                "topico": topico
            }

            if inscricao_existente not in inscricoes:
                inscricoes.append(inscricao_existente)

    def publicar(self, id_publisher, topico, mensagem):

        print(
            f"Recebi publicação: "
            f"{id_publisher} - {topico} - {mensagem}"
        )

        # Procura somente os subscribers inscritos
        # no tópico da mensagem
        for inscricao in inscricoes:

            if inscricao["topico"] == topico:

                id_subscriber = inscricao["subscriber"]

                # Cria um Proxy para realizar o callback remoto
                subscriber = Pyro5.api.Proxy(
                    subscribers[id_subscriber]
                )

                print(
                    f"Encaminhando mensagem para {id_subscriber}"
                )

                subscriber.receber_mensagem(
                    id_publisher,
                    topico,
                    mensagem
                )


# Cria o objeto intermediário
intermediario = Intermediario()


# Cria os tópicos disponíveis
intermediario.criar_topico("noticias")
intermediario.criar_topico("aventura")
intermediario.criar_topico("esportes")


# Cria o Daemon do Pyro5
daemon = Pyro5.api.Daemon()

# Localiza o Name Server
ns = Pyro5.api.locate_ns()

# Registra o intermediário no Daemon
uri = daemon.register(intermediario)

# Registra o intermediário no Name Server
ns.register("Intermediario", uri)

print("Intermediário disponível.")
print("URI:", uri)

# Mantém o intermediário funcionando
daemon.requestLoop()