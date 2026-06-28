import logging
from influxdb_client import Point
from config import INFLUX_BUCKET, INFLUX_ORG
from database_config import write_api

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

