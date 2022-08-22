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
$ pipenv shell
$ jupyter notebook
$ tensorboard --logdir=runs

# with conda environment locally
uses requirements.txt file for dependencies
