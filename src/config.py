import os

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "trabalho-nosql-iot/arthurandrade-caiodaniel-joaopedro"
MQTT_QOS = 1
MQTT_KEEPALIVE = 60

ARQUIVO_DADOS = "dados.json"
LIMITE_TEMPERATURA = 30.0
LIMITE_UMIDADE_MAX = 60.0
LIMITE_UMIDADE_MIN = 30.0
INTERVALO_ENVIO = 5

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8087")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "token_influx")
INFLUX_ORG = os.getenv("INFLUX_ORG", "trabalho-nosql-org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "trabalho-nosql")