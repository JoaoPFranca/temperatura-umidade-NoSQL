from .channels.console import ConsoleAlert
from .channels.discord import DiscordAlert
from config import LIMITE_TEMPERATURA, LIMITE_UMIDADE_MAX, LIMITE_UMIDADE_MIN


class AlertManager:
    def __init__(self):
        self.channels = [ConsoleAlert(), DiscordAlert()]
        self.estado_alerta = {}

    def processar_leitura(self, dados):
        """Avalia limites e dispara notificacoes."""
        temp = dados.get("temperatura")
        umid = dados.get("umidade")
        disp = dados.get("dispositivo", "Desconhecido")

        if disp not in self.estado_alerta:
            self.estado_alerta[disp] = {"temperatura": "NORMAL", "umidade": "NORMAL"}

        # Alertas de Temperatura
        if temp is not None:
            if temp > LIMITE_TEMPERATURA + 5:
                novo_estado = "CRITICO"
            elif temp > LIMITE_TEMPERATURA:
                novo_estado = "AVISO"
            else:
                novo_estado = "NORMAL"

            if novo_estado != self.estado_alerta[disp]["temperatura"]:
                self.estado_alerta[disp]["temperatura"] = novo_estado
                if novo_estado != "NORMAL":
                    self.notificar(f"{novo_estado}: Temperatura anormal. {temp}C no {disp}.", novo_estado,
                                   "temperatura", dados)
                else:
                    self.notificar(f"NORMAL: Temperatura normalizada. {temp}C no {disp}.", "NORMAL", "temperatura",
                                   dados)

        # Alertas de Umidade
        if umid is not None:
            if umid > LIMITE_UMIDADE_MAX + 10 or umid < LIMITE_UMIDADE_MIN - 10:
                novo_estado = "CRITICO"
            elif umid > LIMITE_UMIDADE_MAX or umid < LIMITE_UMIDADE_MIN:
                novo_estado = "AVISO"
            else:
                novo_estado = "NORMAL"

            if novo_estado != self.estado_alerta[disp]["umidade"]:
                self.estado_alerta[disp]["umidade"] = novo_estado
                if novo_estado != "NORMAL":
                    self.notificar(f"{novo_estado}: Umidade anormal. {umid}% no {disp}.", novo_estado, "umidade", dados)
                else:
                    self.notificar(f"NORMAL: Umidade normalizada. {umid}% no {disp}.", "NORMAL", "umidade", dados)

    def notificar(self, msg, nivel, tipo="geral", dados=None):
        for canal in self.channels:
            try:
                canal.enviar(msg, nivel, tipo, dados)
            except Exception as e:
                print(f"Erro no canal {canal.__class__.__name__}: {e}")