import argparse
import json
import logging
import os
from datetime import datetime
from time import sleep

import pandas as pd
import requests

logger = logging.getLogger("streaming_send_data")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def preprocess_data(df, metadata):
    """
    add label column and change path to fname column

    need to have the same preprocessing steps as during training,
    number of features needs to stay the same
    """
    df_lego = pd.merge(df, metadata["minifigure_name"], on="class_id")
    df_lego["labels"] = df_lego["minifigure_name"].apply(lambda x: x.lower())
    df_lego["fname"] = "/home/ubuntu/mlops_zoomcamp_homework/data/" + df_lego.path
    # HOTFIX why needed to remove path containing my user name?
    df_lego["path"] = df_lego["fname"]
    return df_lego


def get_data(data_path):
    """gets data from path, loads it and returns data loader"""
    logger.info("loading data from file path %s", data_path)
    df = pd.read_csv(data_path, encoding="utf8")
    lego_metadata = pd.read_csv(
        os.path.join(os.path.dirname(data_path), "metadata.csv"), index_col=0
    )
    df_lego = preprocess_data(df, lego_metadata)
    return df_lego


def send_data(data_path):
    """send one image per sencond"""
    df = get_data(data_path)
    df = df.reset_index()  # make sure indexes pair with number of rows

    for index, row in df.iterrows():
        print(index)
        print(row.to_json(orient="columns"))
        print(json.dumps(row.to_json(orient="columns")))
        print(
            "address "
            + "http://"
            + os.getenv("FLASK_ADDRESS", "127.0.0.1")
            + ":9696/predict"
        )
        resp = requests.post(
            "http://" + os.getenv("FLASK_ADDRESS", "127.0.0.1") + ":9696/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(row.to_json(orient="columns")),
            timeout=10,
        ).json()
        # with open(row["path"], "rb") as image_file:
        #    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        # request_dict = {"image_utf8_base64": encoded_string, "label": row["labels"]}
        # resp = requests.post("http://127.0.0.1:9696/predict",
        #                     headers={"Content-Type": "application/json"},
        #                     data=json.dumps(request_dict)).json()

        print(f"predicted minifigure class: {resp['y_pred']}")
        print(f"label of minifigure class: {resp['labels']}")
        sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="prediction of values for production test,"
        + "data will be loaded from data root path used during model training"
        + " and send one by one each second to request preditions"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        help="path to csv of data to predict",
        default="/home/ubuntu/mlops_zoomcamp_homework/data/test.csv",
    )
    args = parser.parse_args()
    send_data(args.data_path)
