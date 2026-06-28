class ConsoleAlert:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def enviar(self, mensagem, nivel="AVISO", tipo="geral", dados=None):
        if nivel == "NORMAL":
            cor = self.GREEN
        elif nivel == "AVISO":
            cor = self.YELLOW
        else:
            cor = self.RED

        print(f"{cor}{self.BOLD}[{nivel} - {tipo.upper()}] {mensagem}{self.RESET}")