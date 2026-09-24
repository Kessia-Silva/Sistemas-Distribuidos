import Pyro5.api

conteudos = [
    {"Publisher": "P1", "topico": "noticias", "mensagem": "nova aula disponivel"},
    {"Publisher": "P2", "topico": "aventura", "mensagem": "aventura publicada"},
    {"Publisher": "P3", "topico": "esportes", "mensagem": "novo jogador contratado"},
]



@Pyro5.api.expose
class Publisher:
    def publicar(self, idPublisher, topico, mensagem):
         intermediario.publicar(idPublisher,topico,mensagem)


# Localiza o intermediário
intermediario = Pyro5.api.Proxy("PYRONAME:Intermediario")

# Cria o Publisher
publisher = Publisher()


# Publica os conteúdos
for conteudo in conteudos:

    publisher.publicar(
        conteudo["Publisher"],
        conteudo["topico"],
        conteudo["mensagem"]
    )
