import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.task_create_request import TaskCreateRequest
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

def setup_lifecycle():
    # 1. Recuperar o ID da Organização
    orgs_api = client.organizations_api()
    orgs = orgs_api.find_organizations(org=INFLUX_ORG)
    if not orgs:
        logger.error("Organização não encontrada!")
        return
    org_id = orgs[0].id

    # 2. Configurar Retenção no bucket atual (ex: reduzir para 7 dias)
    buckets_api = client.buckets_api()
    bucket = buckets_api.find_bucket_by_name(INFLUX_BUCKET)
    if bucket:
        # A retenção é dada em segundos (7 dias * 24 h * 60 m * 60 s)
        bucket.retention_rules = [{"everySeconds": 7 * 24 * 60 * 60, "type": "expire"}]
        buckets_api.update_bucket(bucket)
        logger.info(f"Política de retenção de 7 dias aplicada ao bucket '{INFLUX_BUCKET}'.")
    
    # 3. Criar bucket de downsampling (agregação de longo prazo, ex: reter por 1 ano)
    downsample_bucket_name = f"{INFLUX_BUCKET}-downsampled"
    downsample_bucket = buckets_api.find_bucket_by_name(downsample_bucket_name)
    if not downsample_bucket:
        buckets_api.create_bucket(bucket_name=downsample_bucket_name, org=INFLUX_ORG, retention_rules=[{"everySeconds": 365 * 24 * 60 * 60, "type": "expire"}])
        logger.info(f"Bucket de downsampling '{downsample_bucket_name}' criado com retenção de 1 ano.")
    else:
        logger.info(f"Bucket '{downsample_bucket_name}' já existe.")
    
    # 4. Criar Task de Downsampling no banco
    tasks_api = client.tasks_api()
    tasks = tasks_api.find_tasks(org_id=org_id)
    
    task_name = "downsample_1h"
    task_exists = any(t.name == task_name for t in tasks)
    
    if not task_exists:
        flux_query = f'''
        option task = {{name: "{task_name}", every: 1h}}
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -1h)
            |> filter(fn: (r) => r._measurement == "ambiente")
            |> aggregateWindow(every: 1h, fn: mean)
            |> to(bucket: "{downsample_bucket_name}", org: "{INFLUX_ORG}")
        '''
        
        req = TaskCreateRequest(
            org_id=org_id,
            flux=flux_query,
            status="active"
        )
        try:
            tasks_api.create_task(req)
            logger.info(f"Task de downsampling '{task_name}' criada no InfluxDB. Ela rodará a cada 1 hora.")
        except Exception as e:
            logger.error(f"Erro ao criar task: {e}")
    else:
        logger.info(f"Task de downsampling '{task_name}' já existe no InfluxDB.")

if __name__ == "__main__":
    logger.info("Iniciando setup das politicas de ciclo de vida do InfluxDB...")
    setup_lifecycle()
