# mlops_zoomcamp_homework
Homeworks and project of mlops_zoomcamp https://github.com/DataTalksClub/mlops-zoomcamp

The following parts are referring to the project of the course. Find in in folder [06_project](06_project).

# problem description
Your customer is a company which sells minifigures and experiences a high number of returns. Returned minifigures might not have an undamaged packaging. Therefore, all minifigures are firstly put in one large box. Your task is now to classify these minifigures to enable the customer to pack the minifigures in the correct new packaging.

Training data: https://www.kaggle.com/datasets/ihelon/lego-minifigures-classification

Label: Names of minifigures

# solution overview
![solution_overview](./images/process_overview.png)

# get started
1) get develop environment
    1) ```$ git clone git@github.com:xydo1990/mlops_zoomcamp_homework.git```
    2) ```$ cd mlops_zoomcamp_homework```
    3) ```$ pipenv install```
    4) ```$ pipenv shell```
1) get data from kaggle
    * download with script
        1) follow https://www.kaggle.com/general/74235 to create kaggle API key file kaggle.json
        2) use [06_project/src/get_data.py](06_project/src/get_data.py)
    * download manually at https://www.kaggle.com/datasets/ihelon/lego-minifigures-classification and copy to 06_project/data
2) feeling for dataset: [06_project/src/test.ipynb](06_project/src/test.ipynb)
3) start mlflow tracking server
    * locally with ```$ mlflow server --backend-store-uri sqlite:///backend.db --default-artifact-root ./ --host YOUR_IP```
    * (preferred) remotely: follow steps in mlflow tracking server section
3) train the model: [06_project/src/train_model.py](06_project/src/train_model.py)
    1) adapt TRACKING_SERVER_HOST in train_model.py with your remote AWS instance for tracking config (note: Here two different instances are used)
    2) edit ~/.aws/config with your aws account settings
    4) run training with: ```$ 06_project/src/train_model.py --tracking_server=YOUR_SERVER```
5) deployment streaming and batch mode with docker containers
    1) copy [sample.env](sample.env) to .env with ```$ cp sample.env .env```
    2) adapt values according to your setup in .env ```$ nano .env```
    3) build images and start docker containers ```$ docker-compose up -d --build```

# content of project
* problem description
* capable of deploying in the cloud
* experiment tracking and model registry
* workflow orchestration with prefect
* model deployment in batch and streaming mode
* basic model monitoring
* best practices
    * testing
        * unittest
        * integration_test
    * linter and code formatter used
    * makefile
    * pre-commit hooks
    * CI pipeline


# installation aws
0) installation, including aws cloud instance and s3 storage
    1) ```$ sudp apt-get update```
    2) ```$ pip install --upgrade pip```
    3) ```$ pip3 install pipenv```
    4) ```$ sudo apt install awscli```
    5) ```$ aws configure```  # enter your aws credentials
    6) ```$ sudo install docker-compose```

## installation jupyter notebook
4) for jupyter notebook
    1) python -m ipykernel install --user --name=mlops_zoomcamp_homework
    2) for help see
        * https://dataschool.com/data-modeling-101/running-jupyter-notebook-on-an-ec2-server/
        * https://medium.com/@EdwardCrowder/mlops-zoomcamp-2022-ff12dda6b5cc

## mlflow tracking server
2) mlflow tracking server with remote s3
    1) activate env by: ```$ pipenv shell```
    1) follow steps in this video (scenario 3 to setup remote instance, s3 instance and database https://www.youtube.com/watch?v=1ykg4YmbFVA&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK)
    1) in download folder: connect to aws instance with connection settings copied to terminal
    1) on instance ```$ mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:PASSWORD@DATABASE_IP:5432/mlflow_db --default-artifact-root s3://BUCKET_NAME```
        1) name of s3 bucket BUCKET_NAME
        2) user mlflow
        3) db mlflow_db
        4) mlflow-postgresDB endpoint DATABASE_IP
    5) access tracking server UI: INSTANCE_IP:5000

# check runs
1) ```$ pipenv shell```
2) run jupyter notebook to the end
2) go to folder 06_projects ```$ cd 06_project```
3) check runs by ```$ mlflow ui```

## local mlflow tracking server
1) in 06_project
2) ```$ mlflow server --backend-store-uri sqlite:///backend.db --default-artifact-root ./ --host YOUR_IP```


### after stopping the instances
#### on mlflow instance
1) on instance ```$ mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:PASSWORD@DATABASE_IP:5432/mlflow_db --default-artifact-root s3://BUCKET_NAME```
#### on computation instance
1) add ssh config in ~/.ssh/config for AWS
2) adapt TRACKING_SERVER_HOST in train_model.py with your remote AWS instance for tracking config (note: Here two different instances are used)
3) edit ~/.aws/config with your aws account settings
3) in terminal go to 06_project folder
4) run train_model.py


# tests
## unittests
execute with
1) go to 06_project folder
2) ```$ python -m unittest tests/unittests.py```

## integration_tests
execute with
1) go to 06_project folder
2) ```$ chmod +x tests/integration_test.sh```
3) ```$ ./tests/integration_tests.sh```

# makefile, pre-commit hooks
requirements
1) ```$ sudo apt install make```
2) ```$ sudo apt install make-guile```
3) go to 06_project folder
4) run setup (as well for pre-commit hooks) with ```$ make setup```

# Prefect setup
on remote aws
1) ```$ prefect config set PREFECT_ORION_UI_API_URL="https://<external_IP>:4200/api"```
2) ```$prefect orion start --host 0.0.0.0```
3) ```$prefect storage create```
4) select S3 AWS

on local
1) ```$ prefect config set PREFECT_ORION_UI_API_URL="https://<external_IP>:4200/api"```
2) in project_06 folder run ```$ python src/batch_prefect_flow.py```
3) ```$ prefect deployment create src/batch_prefect_deployment.py```

on prefect UI
1) create Work Queue with deployment


# streaming
##  without docker
1) start docker-compose file in repo root directory with $ docker-compose up -d
    * mlflow registry
    * mongo DB
    * evidently service
2) ```$ docker stop prediction_service```
3) use localhost in following variables:
    MONGODB_ADDRESS="mongodb://localhost:27017"
    EVIDENTLY_SERVICE_ADDRESS = os.getenv(
    "EVIDENTLY_SERVICE", "http://localhost:8085"
4) go to prediction_service folder and run ```$ python streaming_send_data.py```

## with docker env
1) start docker-compose file in repo root directory with ```$ docker-compose up -d```
2) TODO
4) go to prediction_service folder and run ```$ python streaming_send_data.py```


# credits
https://www.kaggle.com/code/janweberml/lego-minifigures-classification-for-beginner/edit

# TODOs
1) monitoring for project
2) CICD (later)
3) streaming in docker
4) check s3 connection pool full warning for batch_docker.py
5) homework 05: finish
6) minimal example with downloaded model (without mlflow tracking server)
