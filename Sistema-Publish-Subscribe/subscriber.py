import Pyro5.api


@Pyro5.api.expose
class Subscriber:

    # Callback chamado remotamente pelo intermediário
    def receber_mensagem(self, id_publisher, topico, mensagem):
        print("\n[Mensagem recebida]")
        print(f"Publisher: {id_publisher}")
        print(f"Tópico: {topico}")
        print(f"Mensagem: {mensagem}")


# Cria o objeto Subscriber
subscriber = Subscriber()

# Cria o Daemon do Pyro5
daemon = Pyro5.api.Daemon()

# Localiza o Name Server
ns = Pyro5.api.locate_ns()

# Registra o Subscriber no Daemon
uri = daemon.register(subscriber)

# Identificador do Subscriber
id_subscriber = input(
    "Digite o identificador do Subscriber (ex: S1): "
)

# Registra o Subscriber no Name Server
ns.register(id_subscriber, uri)

# Localiza o intermediário
intermediario = Pyro5.api.Proxy("PYRONAME:Intermediario")

# Registra o Subscriber no intermediário,
# enviando sua URI para permitir o callback remoto
intermediario.registrar_subscriber(id_subscriber, uri)


# Tópicos disponíveis para inscrição
topicos = {
    "1": "noticias",
    "2": "aventura",
    "3": "esportes"
}

print("\n=== Inscrição do Subscriber ===")
print("Escolha os tópicos que deseja acompanhar:")
print("1 - noticias")
print("2 - aventura")
print("3 - esportes")

escolhas = input(
    "\nDigite os números dos tópicos separados por espaço: "
)

# Registra as inscrições escolhidas no intermediário
for escolha in escolhas.split():

    if escolha in topicos:
        topico = topicos[escolha]

        intermediario.inscrever(
            id_subscriber,
            topico
        )

        print(f"Inscrito no tópico: {topico}")

    else:
        print(f"Opção inválida: {escolha}")


print(
    f"\nSubscriber {id_subscriber} aguardando mensagens..."
)

# Mantém o Subscriber ativo para receber callbacks
daemon.requestLoop()