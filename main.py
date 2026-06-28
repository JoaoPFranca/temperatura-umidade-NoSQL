import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from alerts.manager import AlertManager
from mqtt.subscriber import Subscriber

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
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
