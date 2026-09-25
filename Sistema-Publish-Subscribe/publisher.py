import Pyro5.api


# Notícias disponíveis para publicação
conteudos = [
    {
        "publisher": "P1",
        "topico": "noticias",
        "mensagem": "Universidades anunciam novas oportunidades de pesquisa e extensão para estudantes."
    },
    {
        "publisher": "P2",
        "topico": "noticias",
        "mensagem": "Evento acadêmico reúne estudantes e pesquisadores para discutir inovação e tecnologia."
    },
    {
        "publisher": "P3",
        "topico": "aventura",
        "mensagem": "Trilha ecológica é inaugurada e atrai visitantes em busca de novas experiências."
    },
    {
        "publisher": "P4",
        "topico": "aventura",
        "mensagem": "Expedição explora uma nova região e registra paisagens ainda pouco conhecidas."
    },
    {
        "publisher": "P5",
        "topico": "esportes",
        "mensagem": "Equipe anuncia novo reforço para a próxima temporada do campeonato."
    },
    {
        "publisher": "P6",
        "topico": "esportes",
        "mensagem": "Competição universitária reúne atletas de diferentes instituições neste fim de semana."
    }
]


# Localiza o intermediário pelo Name Server
intermediario = Pyro5.api.Proxy("PYRONAME:Intermediario")


while True:

    print("\n========== CENTRAL DE NOTÍCIAS ==========")

    for i, conteudo in enumerate(conteudos, start=1):
        print(
            f"{i} - [{conteudo['topico'].upper()}] "
            f"{conteudo['mensagem']}"
        )

    print("0 - Sair")

    escolha = input("\nEscolha uma notícia para publicar: ")

    if escolha == "0":
        print("\nPublisher encerrado.")
        break

    if escolha.isdigit() and 1 <= int(escolha) <= len(conteudos):

        conteudo = conteudos[int(escolha) - 1]

        intermediario.publicar(
            conteudo["publisher"],
            conteudo["topico"],
            conteudo["mensagem"]
        )

        print(
            f"\n[Publicada] "
            f"{conteudo['publisher']} → {conteudo['topico']}"
        )

        continuar = input(
            "\nDeseja publicar outra notícia? (s/n): "
        ).lower()

        if continuar != "s":
            print("\nPublisher encerrado.")
            break

    else:
        print("\nOpção inválida. Escolha uma notícia da lista.")