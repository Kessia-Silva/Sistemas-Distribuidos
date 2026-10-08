import Pyro5.api

# apenas inicia o Name Server
if __name__ == "__main__":
    print("Iniciando servidor de nomes Pyro5...")

    Pyro5.api.start_ns_loop()