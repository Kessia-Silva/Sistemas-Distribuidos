import Pyro5.api

topicos = []
subscriber = []
inscricoes = []

@Pyro5.api.expose
class Intermediario:

    def criar_topico(self, nome):
        topicos.append(nome)

    def registrar_subscriber(self, id_subscriber):
        subscriber.append(id_subscriber)

    # Se registra no topico que deseja (ex: noticia esporte)
    def inscrever(self, id_subscriber, topico):
        inscricoes.append({
        "subscriber": id_subscriber,
        "topico": topico
    })

    def publicar(self, id_publisher, topico, mensagem):
        for inscricao in inscricoes:
            if inscricao["topico"] == topico:
                subscriber.enviarMensagem(id_publisher, topico, mensagem)


publisher = Pyro5.api.Proxy("PYRONAME:Publicador")

subscriber = Pyro5.api.Proxy("PYRONAME:Inscrito")
