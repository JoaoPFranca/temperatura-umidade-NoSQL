import paho.mqtt.client as mqtt
import json

broker = "test.mosquitto.org"
topico = "trabalho-nosql-iot/arthurandrade-caiodaniel-joaopedro"

client = mqtt.Client()
client.connect(broker, 1883, 60)

payload = json.dumps({
    "device": "sensor-sala",
    "temperatura": 24.5,
    "umidade": 55.0
})

client.publish(topico, payload)
print("Dado enviado simulando o sensor!")