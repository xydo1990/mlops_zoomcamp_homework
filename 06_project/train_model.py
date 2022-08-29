#!/usr/bin/env python
# coding: utf-8

# separately because of multiprocessing
import pandas as pd
import numpy as np
import torch
from fastai.vision.all import *
import random
from torchvision.models import resnet50, ResNet50_Weights
import mlflow
import os


def seed_everything(seed=0):
    """ ensure reproducability by defining random seed """
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def preprocess_data(df, metadata):
    """ add label column and change path to fname column"""
    df_lego = pd.merge(df, metadata['minifigure_name'], on='class_id')
    df_lego['labels'] = df_lego['minifigure_name'].apply(lambda x: x.lower())
    df_lego['fname'] = df_lego['path']
    return df_lego


def data_preprocess_handler(path):
    df = pd.read_csv(os.path.join(path, 'index.csv'), index_col=1)
    lego_metadata = pd.read_csv(os.path.join(path, 'metadata.csv'), index_col=0)
    df_lego = preprocess_data(df, lego_metadata)
    data = ImageDataLoaders.from_df(df_lego, path, valid_pct=0.10,
                                    item_tfms=Resize(412),
                                    bs=10, num_workers=0, label_col="labels")
    return data


if __name__ == "__main__":
    seed_everything()

    os.environ["AWS_PROFILE"] = "default"  # fill in with your AWS profile.
    TRACKING_SERVER_HOST = "ec2-18-132-211-111.eu-west-2.compute.amazonaws.com"  # fill in with the public DNS of the EC2 instance
    mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
    os.environ['TORCH_HOME'] = 'models\\resnet'  # setting the environment variable
    path = os.path.join(os.getcwd(), 'data')  # path to downloaded dataset
    torch.set_num_threads(3)  # adapt to your hardware setup

    mlflow.set_experiment("project_resnet50_parallel")

    mlflow.fastai.autolog()

    with mlflow.start_run():
        data = data_preprocess_handler(path)

        params = {"lr1": 1e-3, "lr2": 1e-1, "random_seed": 0}
        mlflow.log_params(params)

        learn = vision_learner(data, resnet50, metrics=[error_rate, accuracy], model_dir=Path(os.path.join(os.getcwd(),
                                                                                                           "models",
                                                                                                           "resnet")),
                               path=Path(""
                                         "."))
        learn.fit_one_cycle(100, slice(params["lr1"], params["lr2"]), cbs=[EarlyStoppingCallback(patience=2),
                                                                           SaveModelCallback(fname='model_best'),
                                                                           ReduceLROnPlateau()])