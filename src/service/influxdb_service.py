import logging
from influxdb_client import Point
from config import INFLUX_BUCKET, INFLUX_ORG
from database_config import write_api, client

logger = logging.getLogger(__name__)

def inserir_data_dht(device, temperatura, umidade):
    try:
        point = (Point('ambiente')
                 .tag('device', device)
                 .field('temperatura', temperatura)
                 .field('umidade', umidade))
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        logger.info(f"Dados guardados no banco com sucesso: {point}")
    except Exception as e:
        logger.error(e)

def consultar_dados(dispositivo: str, horas: int = 1):
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -{horas}h)
      |> filter(fn: (r) => r._measurement == "ambiente")
      |> filter(fn: (r) => r.device == "{dispositivo}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
    """
    try:
        query_api = client.query_api()
        result = query_api.query(org=INFLUX_ORG, query=query)
        
        registros = []
        for table in result:
            for record in table.records:
                registros.append({
                    "time": record.get_time().isoformat(),
                    "temperatura": record.values.get("temperatura"),
                    "umidade": record.values.get("umidade")
                })
        return registros
    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        return []

def consultar_dados_intervalo(dispositivo: str, inicio: str, fim: str):
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: {inicio}, stop: {fim})
      |> filter(fn: (r) => r._measurement == "ambiente")
      |> filter(fn: (r) => r.device == "{dispositivo}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
    """
    try:
        query_api = client.query_api()
        result = query_api.query(org=INFLUX_ORG, query=query)
        registros = [{"time": rec.get_time().isoformat(), "temperatura": rec.values.get("temperatura"), "umidade": rec.values.get("umidade")} for tab in result for rec in tab.records]
        return registros
    except Exception as e:
        logger.error(f"Erro na consulta por intervalo: {e}")
        return []

def consultar_dados_agregados(dispositivo: str, horas: int = 24, janela: str = "1h"):
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -{horas}h)
      |> filter(fn: (r) => r._measurement == "ambiente")
      |> filter(fn: (r) => r.device == "{dispositivo}")
      |> aggregateWindow(every: {janela}, fn: mean, createEmpty: false)
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
    """
    try:
        query_api = client.query_api()
        result = query_api.query(org=INFLUX_ORG, query=query)
        registros = [{"time": rec.get_time().isoformat(), "temperatura_media": rec.values.get("temperatura"), "umidade_media": rec.values.get("umidade")} for tab in result for rec in tab.records]
        return registros
    except Exception as e:
        logger.error(f"Erro na consulta agregada: {e}")
        return []

def consultar_dados_media_movel(dispositivo: str, horas: int = 1, n_pontos: int = 5):
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -{horas}h)
      |> filter(fn: (r) => r._measurement == "ambiente")
      |> filter(fn: (r) => r.device == "{dispositivo}")
      |> movingAverage(n: {n_pontos})
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
    """
    try:
        query_api = client.query_api()
        result = query_api.query(org=INFLUX_ORG, query=query)
        registros = [{"time": rec.get_time().isoformat(), "temperatura_media_movel": rec.values.get("temperatura"), "umidade_media_movel": rec.values.get("umidade")} for tab in result for rec in tab.records]
        return registros
    except Exception as e:
        logger.error(f"Erro na consulta media movel: {e}")
        return []

def deletar_dados(dispositivo: str, inicio: str, fim: str):
    try:
        delete_api = client.delete_api()
        predicate = f'_measurement="ambiente" AND device="{dispositivo}"'
        delete_api.delete(inicio, fim, predicate, bucket=INFLUX_BUCKET, org=INFLUX_ORG)
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar dados: {e}")
        return False

def atualizar_data_dht(device: str, temperatura: float, umidade: float, timestamp: str):
    try:
        point = (Point('ambiente')
                 .tag('device', device)
                 .field('temperatura', temperatura)
                 .field('umidade', umidade)
                 .time(timestamp)) # A mágica da sobreposição acontece aqui
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar dados: {e}")
        return False