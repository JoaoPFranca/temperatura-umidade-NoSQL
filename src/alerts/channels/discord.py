import requests
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DiscordAlert:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_ALERT_WEBHOOK")
        self.validar()

    def validar(self):
        """Valida a conectividade com o Webhook."""
        if not self.webhook_url:
            logger.error("Webhook Discord ausente no .env")
            return
        try:
            if requests.get(self.webhook_url).status_code == 200:
                logger.info("Webhook Discord validado com sucesso.")
        except:
            logger.error("Falha ao validar conexao com Discord.")

    def enviar(self, mensagem, nivel="AVISO", tipo="geral", dados=None):
        """Envia card formatado para o Discord."""
        if not self.webhook_url: return

        if nivel == "NORMAL":
            color = 65280
            titulo = "SISTEMA NORMALIZADO"
        elif nivel == "AVISO":
            color = 16776960
            titulo = "ALERTA DE MONITORAMENTO"
        else:
            color = 15548997
            titulo = "ALERTA CRITICO DETECTADO"

        fields = [
            {
                "name": "Nivel de Prioridade",
                "value": nivel,
                "inline": True
            },
            {
                "name": "Status do Sistema",
                "value": "Monitorando" if nivel in ["NORMAL", "AVISO"] else "Acao Necessaria",
                "inline": True
            }
        ]

        if tipo == "umidade" and dados and "umidade" in dados:
            fields.append({
                "name": "Umidade",
                "value": f"{dados['umidade']}%",
                "inline": True
            })
        elif tipo == "temperatura" and dados and "temperatura" in dados:
            fields.append({
                "name": "Temperatura",
                "value": f"{dados['temperatura']}C",
                "inline": True
            })

        fields.append({
            "name": "Local/Dispositivo",
            "value": dados.get("dispositivo", "Sensor IoT - Area Interna") if dados else "Sensor IoT - Area Interna",
            "inline": False
        })

        payload = {
            "embeds": [
                {
                    "title": titulo,
                    "description": mensagem,
                    "color": color,
                    "fields": fields,
                    "footer": {
                        "text": "Sistema de Monitoramento IoT - Disciplina Consumer-TCIoT"
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Erro ao enviar para Discord: {e}")