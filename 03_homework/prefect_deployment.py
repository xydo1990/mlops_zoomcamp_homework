from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner
from prefect.deployments import DeploymentSpec


DeploymentSpec(
    flow_location="prefect_flow.py",
    name="cron_deployment",
    schedule=CronSchedule(cron="0 9 15 * *", timezone="America/New_York"),
    flow_runner=SubprocessFlowRunner(),
    tags=["ml"]
)
