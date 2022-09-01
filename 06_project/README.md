# problem description
Your customer is a company which sells minifigures and experiences a high number of returns. Returned minifigures might not have an undamaged packaging. Therefore, all minifigures are firstly put in one large box. Your task is now to classify these minifigures to enable the customer to pack the minifigures in the correct new packaging.

Training data: https://www.kaggle.com/datasets/ihelon/lego-minifigures-classification

Label: Names of minifigures

# solution overview
![solution_overview](../images/process_overview.png)

# get started
0) installation, including aws cloud instance and s3 storage
1) feeling for dataset -> jupyter notebook 
2) train_model.py
3) deployment of model in batch mode via: batch.py

# installation
## how to setup jupyter notebook in aws
https://dataschool.com/data-modeling-101/running-jupyter-notebook-on-an-ec2-server/
https://medium.com/@EdwardCrowder/mlops-zoomcamp-2022-ff12dda6b5cc

## dataset
https://www.kaggle.com/datasets/ihelon/lego-minifigures-classification

### get from kaggle
1) follow https://www.kaggle.com/general/74235 to create kaggle API key file kaggle.json
2) install with $ pipenv install kaggle
3) in batch.py the data will be downloaded from kaggle

## model training code
https://www.kaggle.com/code/janweberml/lego-minifigures-classification-for-beginner/edit


## prepare aws for code 
pip3 install pipenv
git clone git@github.com:xydo1990/mlops_zoomcamp_homework.git
cd mlops_zoomcamp_homework

## on aws
sudp apt-get update
pip install --upgrade pip
python -m venv mlops_zoomcamp_homework  # create venv
    source mlops_zoomcamp_homework/bin/activate  # for unix users
    mlops_zoomcamp_homework/bin/activate  # for windows users
pip install -r requirements.txt
pip install fastai --upgrade
python -m ipykernel install --user --name=mlops_zoomcamp_homework
git config --global user.name "YOUR_NAME"
git config --global user.email "your_email"
sudo apt install awscli
aws configure  # enter your aws credentials

## with pipenv locally
## python 3.9
## use ubuntu for plug and play setup
$ pipenv shell
$ jupyter notebook
$ tensorboard --logdir=runs

# check runs
1) $ pipenv shell
2) run jupyter notebook to the end
2) go to folder 06_projects '''$cd 06_project'''
3) check runs by '''$mlflow ui'''

## local mlflow tracking server
1) in 06_project
2) $ mlflow server --backend-store-uri sqlite:///backend.db --default-artifact-root ./ --host YOUR_IP


## remote tracking server
0) activate env by: $ pipenv shell
1) follow steps in this video (scenario 3 to setup remote instance, s3 instance and database https://www.youtube.com/watch?v=1ykg4YmbFVA&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK)
1) in download folder: connect to aws instance with connection settings copied to terminal
1) on instance $  mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:3bxprPbnQiwPB54yBe3b@mlflow-database.cjhtlhjvzym4.eu-west-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-artifacts-remote-xydo
   2) name of s3 bucket mlflow-artifacts-remote-xydo
   2) user mlflow
   3) db mlflow_db
   4) mlflow-postgresDB endpoint mlflow-database.cjhtlhjvzym4.eu-west-2.rds.amazonaws.com
5) access tracking server UI: INSTANCE_IP:5000

### after stopping the instances
#### on mlflow instance
1) on instance $  mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:3bxprPbnQiwPB54yBe3b@mlflow-database.cjhtlhjvzym4.eu-west-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-artifacts-remote-xydo
#### on computation instance
1) add ssh config in ~/.ssh/config for AWS
2) adapt TRACKING_SERVER_HOST in train_model.py with your remote AWS instance for tracking config (note: Here two different instances are used) 
3) edit ~/.aws/config with your aws account settings
3) in terminal go to 06_project folder
4) run train_model.py
5) $ sudo install docker-compose


## TODO upload new created image to Docker hub
docker build -t mlops-zoomcamp-model:v1 .
docker tag mlops-zoomcamp-model:v1 agrigorev/zoomcamp-model:mlops-3.9.7-slim
docker push agrigorev/zoomcamp-model:mlops-3.9.7-slim
