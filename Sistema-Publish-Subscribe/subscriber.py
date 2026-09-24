import Pyro5.api

@Pyro5.api.expose
class Subscriber:
    def receberMenssagem(sef, idPublisher, topico, mensagem):
        print(f'[Mensagem recebida]')
        print(f'idPublisher: {idPublisher}')
        print(f'topico: {topico}')
        print(f'menssagem: {mensagem}')

# Cria o objeto Subscriber
subscriber = Subscriber()

# Cria o Daemon do Pyro5
daemon = Pyro5.api.Daemon()

# Localiza o Name Server
ns = Pyro5.api.locate_ns()

# Registra o Subscriber no Daemon
uri = daemon.register(subscriber)

# Identificador do Subscriber
id_subscriber = "S1"

# Localiza o intermediário
intermediario = Pyro5.api.Proxy("PYRONAME:Intermediario")

# Registra o Subscriber no intermediário
intermediario.registrar_subscriber("S1", uri)

intermediario.inscrever("S1", "noticias")
intermediario.inscrever("S1", "esportes")

# Registra o Subscriber no Name Server
ns.register(id_subscriber, uri)

print(f"Subscriber {id_subscriber} aguardando mensagens...")

# Mantém o Subscriber funcionando
daemon.requestLoop()