import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, ARQUIVO_DADOS, MQTT_QOS, MQTT_KEEPALIVE

logger = logging.getLogger(__name__)


class Subscriber:
    def __init__(self, alert_manager):
        self.alert_manager = alert_manager
        self.client = mqtt.Client()
        self.client.on_connect = self.ao_conectar
        self.client.on_message = self.ao_receber_mensagem

    def salvar(self, payload):
        try:
            dados = []
            try:
                with open(ARQUIVO_DADOS, 'r') as f:
                    dados = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            dados.append(payload)
            with open(ARQUIVO_DADOS, 'w') as f:
                json.dump(dados, f, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar: {e}")

    def ao_conectar(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Conectado ao Broker.")
            client.subscribe(MQTT_TOPIC, qos=MQTT_QOS)
        else:
            logger.error(f"Falha na conexao: {rc}")

    def ao_receber_mensagem(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode()
            logger.info(f"Dados recebidos: {payload_str}")

            try:
                data = json.loads(payload_str)
                if 'timestamp' not in data:
                    data['timestamp'] = datetime.now().isoformat()

                self.salvar(data)
                self.alert_manager.processar_leitura(data)
            except json.JSONDecodeError:
                logger.warning("Payload invalido (nao-JSON).")
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")

    def iniciar(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        self.client.loop_forever()