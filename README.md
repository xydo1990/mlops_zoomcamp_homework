# mlops_zoomcamp_homework
Homework of mlops_zoomcamp https://github.com/DataTalksClub/mlops-zoomcamp


how to start mlflow server: mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --host 0.0.0.0


prefect docker run -it --rm -p 4200:4200 prefecthq/prefect:2.0b5-python3.8 prefect orion start --host=0.0.0.0