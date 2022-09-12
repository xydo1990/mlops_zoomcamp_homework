# mlops_zoomcamp_homework
Homework of mlops_zoomcamp https://github.com/DataTalksClub/mlops-zoomcamp


how to start mlflow server: mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --host 0.0.0.0


prefect docker run -it --rm -p 4200:4200 prefecthq/prefect:2.0b5-python3.8 prefect orion start --host=0.0.0.0


# streaming
##  without docker
1) start docker-compose file in repo root directory with $ docker-compose up -d
    * mlflow registry
    * mongo DB
    * evidently service
2) $ docker stop prediction_service
3) use localhost in following variables:
    MONGODB_ADDRESS="mongodb://localhost:27017"
    EVIDENTLY_SERVICE_ADDRESS = os.getenv(
    "EVIDENTLY_SERVICE", "http://localhost:8085"
4) go to prediction_service folder and run $ python streaming_send_data.py

## with docker env
1) start docker-compose file in repo root directory with $ docker-compose up -d
2) TODO
3) TODO
4) go to prediction_service folder and run $ python streaming_send_data.py
