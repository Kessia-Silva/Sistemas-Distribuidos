
# Configurações globais do experimento.

class Configuracao:
    # Nomes dos processos distribuídos.
    PROCESSOS = ["p1", "p2", "p3", "p4"]

    # Tempo de geração de eventos, em segundos.
    DURACAO = 30

    # Tempo mínimo e máximo entre eventos locais.
    INTERVALO_MIN = 1
    INTERVALO_MAX = 3

    # Atraso aleatório antes do envio de cada mensagem.
    DELAY_MIN = 0.1
    DELAY_MAX = 1.0

    # Tempo extra para o processo continuar recebendo mensagens
    # depois que terminar a geração de eventos.
    MARGEM_FINAL = 3
