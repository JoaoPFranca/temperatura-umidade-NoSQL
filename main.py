import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from alerts.manager import AlertManager
from mqtt.subscriber import Subscriber
from service.influxdb_service import consultar_dados

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando monitoramento IoT...")
    alert_manager = AlertManager()
    subscriber = Subscriber(alert_manager)
    subscriber.iniciar_background()
    app.state.subscriber = subscriber
    try:
        yield
    finally:
        subscriber.parar()


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "Monitoramento IoT Ativo", "banco": "InfluxDB"}

@app.get("/api/dados/{dispositivo}")
async def get_dados_dispositivo(dispositivo: str, horas: int = 1):
    dados = consultar_dados(dispositivo, horas)
    return {
        "dispositivo": dispositivo,
        "periodo_horas": horas,
        "total_registros": len(dados),
        "historico": dados
    }
