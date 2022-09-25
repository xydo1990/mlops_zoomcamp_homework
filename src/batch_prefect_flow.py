#!/usr/bin/env python
# coding: utf-8

import argparse
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastai.vision.all import *
from prefect import flow, get_run_logger, task
from prefect.task_runners import SequentialTaskRunner
from sklearn.metrics import accuracy_score

import mlflow

### goal: predict new batch of data and store predictions to file for analysis
# loads model and data from file in docker-compose.yml


@task
def store_predictions(df, y_pred, output_file, y=None):
    """
    stores predictions to output_file in parquet format

    stores labels as well if present
    """
    logger = get_run_logger()
    df_result = pd.DataFrame()
    df_result["fname"] = df["fname"]
    df_result["y_pred"] = y_pred
    if y is not None:
        df_result["label"] = y

    # only needed if storing on local file system:
    dir_name = os.path.dirname(output_file)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    logger.info("storing predictions to file" + output_file)
    df_result.to_parquet(output_file, engine="pyarrow", compression=None, index=False)
    logger.info("size of saved data:" + str(os.path.getsize(output_file) / 1000000))


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


@task
def get_data(data_path):
    """gets data from path, loads it and returns data loader"""
    logger = get_run_logger()
    logger.info("loading data from file path:" + data_path)
    df = pd.read_csv(data_path, encoding="utf8")
    lego_metadata = pd.read_csv(
        os.path.join(os.path.dirname(data_path), "metadata.csv"), index_col=0
    )
    df_lego = preprocess_data(df, lego_metadata)
    return df_lego


@task
def get_learner(model_run, tracking_server_ip, tracking_server_port):
    """get model from mlflow model registry"""
    logger = get_run_logger()
    logger.info(
        "loading model from file %s and uri http://%s:%s"
        % (model_run, tracking_server_ip, tracking_server_port)
    )
    # os.environ["AWS_PROFILE"] = "default"

    mlflow.set_tracking_uri(f"http://{tracking_server_ip}:{tracking_server_port}")
    logger.info(os.path.dirname(os.path.abspath(__file__)))
    learn = mlflow.pyfunc.load_model(
        model_run, dst_path=os.path.dirname(os.path.abspath(__file__))
    )
    return learn


@task
def make_predictions(learn, df):
    """make predictions with data loader using learner"""
    # test_dl = learn.dls.test_dl(test_files)
    # preds, _, decoded = learn.get_preds(dl=test_dl, with_decoded=True)
    y_probs = learn.predict(df)
    y_pred = np.array([np.argmax(i) for sample in np.array(y_probs) for i in sample])
    # return y_pred, np.array(df["class_id"])
    return y_pred


@task
def calculate_metrics(y_pred, y):
    """
    calculate different metrics based on predictions

    metrics are not stored atm
    """
    logger = get_run_logger()
    accuracy = accuracy_score(y, y_pred)
    logger.info("accuracy" + accuracy)


@flow(task_runner=SequentialTaskRunner())
def run_flow(
    data_path, model_run, tracking_server_ip, tracking_server_port, output_file
):
    """handles run of loading model and data, make predictions and store result"""
    logger = get_run_logger()
    logger.info("get data")
    df_lego = get_data(data_path)
    logger.info("get model")
    learner = get_learner(model_run, tracking_server_ip, tracking_server_port)
    logger.info("make predictions")
    # y_pred, y = make_predictions(learner, df_lego)
    y_pred = make_predictions(learner, df_lego)
    y = None  # y = np.array(df_lego["class_id"]) # not working
    logger.info("calculate metrics")
    if y is not None:
        calculate_metrics(y_pred, y)
    logger.info("store predictions")
    store_predictions(df_lego, y_pred, output_file, y)


if __name__ == "__main__":
    load_dotenv()

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
        default="runs:/e1c3003940e14f3f872dea8521bb1cd6/model",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="path of parquet file to store predictions",
        default="/home/ubuntu/mlops_zoomcamp_homework/outputs/batch_predictions.parquet",
    )
    parser.add_argument(
        "--tracking_server_ip",
        type=str,
        help="mlflow tracking server host IP",
        default="localhost",
    )
    parser.add_argument(
        "--tracking_server_port",
        type=int,
        help="mlflow tracking server host port",
        default=5000,
    )
    parser.add_argument(
        "--mlflow_bucket",
        type=str,
        help="AWS S3 bucket name",
        default="YOUR_S3_BUCKET_NAME",
    )
    args = parser.parse_args()

    args.tracking_server_ip = os.getenv("TRACKING_SERVER_HOST", args.tracking_server_ip)
    args.tracking_server_port = os.getenv(
        "TRACKING_SERVER_HOST_PORT", args.tracking_server_port
    )
    args.model_run = os.getenv("MLFLOW_RUN", args.model_run)
    args.mlflow_bucket = os.getenv("MLFLOW_BUCKET_NAME", args.mlflow_bucket)

    run_flow(
        args.data_path,
        args.model_run,
        args.tracking_server_ip,
        args.tracking_server_port,
        args.output_file,
    )
