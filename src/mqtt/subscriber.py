import paho.mqtt.client as mqtt
import json
import logging
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_QOS, MQTT_KEEPALIVE
from service.influxdb_service import inserir_data_dht

logger = logging.getLogger(__name__)

class Subscriber:
    def __init__(self, alert_manager):
        self.alert_manager = alert_manager
        self.client = mqtt.Client()
        self.client.on_connect = self.ao_conectar
        self.client.on_message = self.ao_receber_mensagem

    def ao_conectar(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Conectado ao Broker.")
            client.subscribe(MQTT_TOPIC, qos=MQTT_QOS)
            logger.info(f"Inscrito no topico MQTT: {MQTT_TOPIC}")
        else:
            logger.error(f"Falha na conexao: {rc}")

    def ao_receber_mensagem(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode()
            logger.info(f"Dados recebidos: {payload_str}")

            try:
                data = json.loads(payload_str)
                inserir_data_dht(data['device'], data['temperatura'], data['umidade'])
                self.alert_manager.processar_leitura(data)
            except KeyError as e:
                logger.error(f"Campo ausente no payload MQTT: {e}. Payload: {payload_str}")
            except json.JSONDecodeError:
                logger.warning("Payload invalido (nao-JSON).")
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")

    def iniciar_background(self):
        logger.info(f"Conectando ao MQTT em {MQTT_BROKER}:{MQTT_PORT}...")
        self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        self.client.loop_start()

    def parar(self):
        logger.info("Encerrando subscriber MQTT...")
        self.client.loop_stop()
        self.client.disconnect()
