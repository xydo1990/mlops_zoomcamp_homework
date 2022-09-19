from prefect.deployments import Deployment
from prefect.infrastructure import Process
from prefect.orion.schemas.schedules import CronSchedule

from src.batch_prefect_flow import run_flow

# create prefect deployment of run_flow with CronSchedule
deployment = Deployment.build_from_flow(
    flow=run_flow,
    name="model_deployment_cron",
    schedule=CronSchedule(cron="0 9 15 * *", timezone="Europe/Berlin"),
    infrastructure=Process(),
    work_queue_name="prod",
)
deployment.apply()
