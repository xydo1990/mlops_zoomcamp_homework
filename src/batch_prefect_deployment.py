from prefect.deployments import DeploymentSpec
from prefect.flow_runners import SubprocessFlowRunner
from prefect.orion.schemas.schedules import CronSchedule

DeploymentSpec(
    flow_location="batch_prefect_flow.py",
    name="cron_deployment",
    schedule=CronSchedule(cron="0 9 15 * *", timezone="Europe/Berlin"),
    flow_runner=SubprocessFlowRunner(),
    tags=["ml"],
)
