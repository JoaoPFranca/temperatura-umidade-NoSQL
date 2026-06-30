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