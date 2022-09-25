from datetime import timedelta

from prefect.deployments import DeploymentSpec
from prefect.flow_runners import SubprocessFlowRunner
from prefect.orion.schemas.schedules import IntervalSchedule

# create prefect deployment of run_flow with CronSchedule
DeploymentSpec(
    flow_location="batch_prefect_flow.py",
    name="model_training",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    flow_runner=SubprocessFlowRunner(),
    tags=["ml"],
)

# deployment = Deployment.build_from_flow(
#    flow=run_flow,
#    name="model_deployment_cron",
#    schedule=CronSchedule(cron="0 9 15 * *", timezone="Europe/Berlin"),
#    infrastructure=Process(),
#    work_queue_name="prod",
# )
# deployment.apply()
