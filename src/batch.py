#!/usr/bin/env python
# coding: utf-8

import argparse
import os

import kaggle
import numpy as np
import pandas as pd
from fastai.vision.all import *
from sklearn.metrics import accuracy_score

import mlflow

### goal: predict new batch of data and store predictions to file for analysis


def store_predictions(df, y_pred, output_file, y=None):
    """
    stores predictions to output_file in parquet format

    stores labels as well if present
    """
    df_result = pd.DataFrame()
    df_result["fname"] = df["fname"]
    df_result["y_pred"] = y_pred
    if y is not None:
        df_result["label"] = y

    dir_name = os.path.dirname(output_file)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    print(f"storing predictions to file {output_file}")
    df_result.to_parquet(output_file, engine="pyarrow", compression=None, index=False)
    print(f"size of saved data: {os.path.getsize(output_file) / 1000000}")


def preprocess_data(df, metadata):
    """
    add label column and change path to fname column

    need to have the same preprocessing steps as during training,
    number of features needs to stay the same
    """
    df_lego = pd.merge(df, metadata["minifigure_name"], on="class_id")
    df_lego["labels"] = df_lego["minifigure_name"].apply(lambda x: x.lower())
    df_lego["fname"] = df_lego.path
    # HOTFIX why needed to remove path containing my user name?
    df_lego["fname"] = df_lego["fname"]

    return df_lego


def get_data(data_path, download=False):
    """gets data from path, loads it and returns data loader"""
    if download:
        print(
            "download data from kaggle, assuming that you have"
            + "authentification key in correct ~/.kaggle/kaggle.json"
        )
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            "ihelon/lego-minifigures-classification",
            path=os.path.dirname(data_path),
            unzip=True,
        )
    else:
        print("use data copy from this repo")

    print(f"loading data from file path: {data_path}")
    df = pd.read_csv(data_path, encoding="utf8")
    lego_metadata = pd.read_csv(
        os.path.join(os.path.dirname(data_path), "metadata.csv"), index_col=0
    )
    df_lego = preprocess_data(df, lego_metadata)
    return df_lego


def get_learner(model_run, tracking_server):
    """get model from mlflow model registry"""
    print(f"loading model from file {model_run}")
    os.environ["AWS_PROFILE"] = "default"
    mlflow.set_tracking_uri(f"http://{tracking_server}:5000")
    print(os.path.dirname(os.path.abspath(__file__)))
    learn = mlflow.pyfunc.load_model(
        model_run, dst_path=os.path.dirname(os.path.abspath(__file__))
    )
    return learn


def make_predictions(learn, df):
    """make predictions with data loader using learner"""
    # test_dl = learn.dls.test_dl(test_files)
    # preds, _, decoded = learn.get_preds(dl=test_dl, with_decoded=True)
    y_probs = learn.predict(df)
    y_pred = np.array([np.argmax(i) for sample in np.array(y_probs) for i in sample])
    return np.array(y_pred), np.array(df["class_id"])


def calculate_metrics(y_pred, y):
    """
    calculate different metrics based on predictions

    metrics are not stored atm
    """
    accuracy = accuracy_score(y, y_pred)
    print(f"accuracy {accuracy}")


def run(args):
    """handles run of loading model and data, make predictions and store result"""
    print("get data")
    df_lego = get_data(args.data_path)
    print("get model")
    learner = get_learner(args.model_run, args.tracking_server)
    print("make predictions")
    y_pred, y = make_predictions(learner, df_lego)
    print("calculate metrics")
    if y is not None:
        calculate_metrics(y_pred, y)
    print("store predictions")
    store_predictions(df_lego, y_pred, args.output_file, y)


if __name__ == "__main__":
    # optional input arguments
    parser = argparse.ArgumentParser(
        description="prediction of values for production test,"
        + "data will be loaded from data root path used during model training"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        help="path to csv of data to predict",
        default="/home/ubuntu/mlops_zoomcamp_homework/data/test.csv",
    )
    parser.add_argument(
        "--model_run",
        type=str,
        help="run of model from mlflow model registry ",
        default="runs:/5e8554e66b654f54ae52a7aeb9ff8b0d/model",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="path of parquet file to store predictions",
        default="/home/ubuntu/mlops_zoomcamp_homework/outputs/batch_predictions.parquet",
    )
    parser.add_argument(
        "--tracking_server",
        type=str,
        help="mlflow tracking server host",
        default="ec2-18-170-72-98.eu-west-2.compute.amazonaws.com",
    )
    args = parser.parse_args()

    run(args)
