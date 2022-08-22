# no tracking server
# local backend and artifact store
import mlflow

print(f"local tracking uri {mlflow.get_tracking_uri()}")
mlflow.list_experiments()

mlflow.set_experiment("project")

with mlflow.start_run():
    pass