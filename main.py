import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from alerts.manager import AlertManager
from mqtt.subscriber import Subscriber
from pydantic import BaseModel
from service.influxdb_service import consultar_dados, consultar_dados_intervalo, deletar_dados, atualizar_data_dht, consultar_dados_agregados, consultar_dados_media_movel

class AtualizacaoSensor(BaseModel):
    temperatura: float
    umidade: float
    timestamp: str

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
    return {"dispositivo": dispositivo, "total_registros": len(dados), "historico": dados}

@app.get("/api/dados/{dispositivo}/intervalo")
async def get_dados_intervalo(dispositivo: str, inicio: str, fim: str):
    # Formato esperado: YYYY-MM-DDTHH:MM:SSZ
    dados = consultar_dados_intervalo(dispositivo, inicio, fim)
    return {"dispositivo": dispositivo, "total_registros": len(dados), "historico": dados}

@app.get("/api/dados/{dispositivo}/resumo")
async def get_dados_resumo(dispositivo: str, horas: int = 24, janela: str = "1h"):
    dados = consultar_dados_agregados(dispositivo, horas, janela)
    return {"dispositivo": dispositivo, "janela": janela, "total_registros": len(dados), "historico_agregado": dados}

@app.get("/api/dados/{dispositivo}/tendencia")
async def get_dados_tendencia(dispositivo: str, horas: int = 1, pontos: int = 5):
    """Nova feature de TSDB: Aplica Média Móvel sobre os últimos N pontos para analisar tendências e suavizar ruídos."""
    dados = consultar_dados_media_movel(dispositivo, horas, pontos)
    return {"dispositivo": dispositivo, "n_pontos": pontos, "total_registros": len(dados), "tendencia": dados}

@app.put("/api/dados/{dispositivo}")
async def atualizar_leitura(dispositivo: str, dados: AtualizacaoSensor):
    sucesso = atualizar_data_dht(dispositivo, dados.temperatura, dados.umidade, dados.timestamp)
    if sucesso:
        return {"mensagem": "Dado sobreposto/atualizado com sucesso."}
    return {"erro": "Falha ao atualizar dado."}

@app.delete("/api/dados/{dispositivo}")
async def deletar_historico(dispositivo: str, inicio: str, fim: str):
    sucesso = deletar_dados(dispositivo, inicio, fim)
    if sucesso:
        return {"mensagem": f"Dados de {dispositivo} deletados no intervalo informado."}
    return {"erro": "Falha ao deletar dados."}
