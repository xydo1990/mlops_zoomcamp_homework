# how to setup jupyter notebook in aws
https://dataschool.com/data-modeling-101/running-jupyter-notebook-on-an-ec2-server/
https://medium.com/@EdwardCrowder/mlops-zoomcamp-2022-ff12dda6b5cc

# dataset
https://www.kaggle.com/datasets/ihelon/lego-minifigures-classification

# model training code
https://www.kaggle.com/code/janweberml/lego-minifigures-classification-for-beginner/edit


# prepare aws for code 
pip3 install pipenv
git clone git@github.com:xydo1990/mlops_zoomcamp_homework.git
cd mlops_zoomcamp_homework

# on aws
sudp apt-get update
pip install --upgrade pip
python -m venv mlops_zoomcamp_homework  # create venv
    source mlops_zoomcamp_homework/bin/activate  # for unix users
    mlops_zoomcamp_homework/bin/activate  # for windows users
pip install -r requirements.txt
pip install fastai --upgrade
python -m ipykernel install --user --name=mlops_zoomcamp_homework

# with pipenv locally
# python 3.9
# use ubuntu for plug and play setup
$ pipenv shell
$ jupyter notebook
$ tensorboard --logdir=runs

# check runs
1) $ pipenv shell
2) run jupyter notebook to the end
2) go to folder 06_projects '''$cd 06_project'''
3) check runs by '''$mlflow ui'''

# local mlflow tracking server
1) in 06_project
2) $ mlflow server --backend-store-uri sqlite:///backend.db --default-artifact-root ./ --host YOUR_IP


# remote tracking server
0) activate env by: $ pipenv shell
1) follow steps in this video (scenario 3 to setup remote instance, s3 instance and database https://www.youtube.com/watch?v=1ykg4YmbFVA&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK)
1) in download folder: connect to aws instance with connection settings copied to terminal
1) on instance $  mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:3bxprPbnQiwPB54yBe3b@mlflow-database.cjhtlhjvzym4.eu-west-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-artifacts-remote-xydo
   2) name of s3 bucket mlflow-artifacts-remote-xydo
   2) user mlflow
   3) db mlflow_db
   4) mlflow-postgresDB endpoint mlflow-database.cjhtlhjvzym4.eu-west-2.rds.amazonaws.com
5) access tracking server UI: INSTANCE_IP:5000

# TODO upload new created image to Docker hub
docker build -t mlops-zoomcamp-model:v1 .
docker tag mlops-zoomcamp-model:v1 agrigorev/zoomcamp-model:mlops-3.9.7-slim
docker push agrigorev/zoomcamp-model:mlops-3.9.7-slim
