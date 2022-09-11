#! app.py

import base64
import io
import json
import logging
import os

import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, request
from PIL import Image
from pymongo import MongoClient

import mlflow

MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27017")
EVIDENTLY_SERVICE_ADDRESS = os.getenv("EVIDENTLY_SERVICE", "http://127.0.0.1:5000")

mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")
collection = db.get_collection("data")
logger = logging.getLogger("streaming_monitoring")


def save_to_db(record, prediction):
    rec = record.copy()
    rec["prediction"] = prediction
    collection.insert_one(rec)


def save_to_evidently_service(record, prediction):
    rec = record.copy()
    rec["prediction"] = prediction
    requests.post(f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/taxi", json=rec, timeout=10)


def get_learner(model_run, tracking_server):
    """get model from mlflow model registry"""
    logger.info(
        "loading model from file %s and uri http://%s:5000"
        % (model_run, tracking_server)
    )
    # os.environ["AWS_PROFILE"] = "default"

    mlflow.set_tracking_uri(f"http://{tracking_server}:5000")
    logger.info(os.path.dirname(os.path.abspath(__file__)))
    learn = mlflow.pyfunc.load_model(
        model_run, dst_path=os.path.dirname(os.path.abspath(__file__))
    )
    return learn


def make_single_prediction(df_row: pd.DataFrame):
    y_probs = learn.predict(df_row)
    print(np.array([np.argmax(i) for sample in np.array(y_probs) for i in sample]))
    y_pred = int(
        np.array([np.argmax(i) for sample in np.array(y_probs) for i in sample])[0]
    )
    label = None
    return y_pred, label


def make_single_prediction_array(image):
    y_probs = learn.predict_array(image)
    y_pred = np.argmax(y_probs)
    label = "unknown, input is image"
    return y_pred, label


def convert_request_to_image_format(image_encoded_as_string):
    # recieves a Base64 String (image)
    # from https://forums.fast.ai/t/how-to-load-a-base64-encoded-image/46385/2
    image_bytes = io.BytesIO(base64.b64decode(image_encoded_as_string))
    image = Image.open(image_bytes)  # this method comes from fastai.vision
    return image


app = Flask("minifigure_prediction_streaming")

# get model from env
learn = get_learner("runs:/5e8554e66b654f54ae52a7aeb9ff8b0d/model", "localhost")


@app.route("/predict", methods=["POST"])
def predict():
    print(request)
    print(request.get_json())
    request_dict = json.loads(request.get_json())
    # request_dict = request.get_json()
    del request_dict["index"]
    df_row = pd.read_json(json.dumps(request_dict), typ="series")
    # df_row['fname'] = df_row.path
    print(df_row.head())
    # return features
    y_pred, _ = make_single_prediction(df_row["path"])
    print("Finished backend prediction")
    return_dict = {"y_pred": y_pred, "labels": df_row["class_id"]}
    print(return_dict)

    # image = convert_request_to_image_format(request_dict["image_utf8_base64"])
    # y_pred, y = make_single_prediction_array(image)
    # print("Finished backend prediction")
    # return_dict = {'minifigure class pred': y_pred, 'target_class': request_dict["label"]}

    # save_to_db(ride, pred_class)
    # save_to_evidently_service(ride, pred_class)

    return jsonify(return_dict)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=9696)
