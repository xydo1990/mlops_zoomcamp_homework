#! app.py

import base64
import io
import logging
import logging.handlers
import os
from logging.config import dictConfig
import json

import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, request
from PIL import Image
from pymongo import MongoClient

import mlflow

MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://localhost:27017")
EVIDENTLY_SERVICE_ADDRESS = os.getenv(
    "EVIDENTLY_SERVICE_ADDRESS", "http://localhost:8085"
)

mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")
collection = db.get_collection("data")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {"class": "logging.StreamHandler", "formatter": "default"}
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)

handler = logging.handlers.SysLogHandler(address="/dev/log")
handler.setFormatter(logging.Formatter("flask [%(levelname)s] %(message)s"))

app = Flask(__name__)
app.logger.addHandler(handler)

# logging.basicConfig(filename="record.log", level=logging.DEBUG)
# app = Flask("minifigure_prediction_streaming")


def save_to_db(record, prediction):
    rec = record.copy()
    rec["prediction"] = prediction
    collection.insert_one(rec)


def save_to_evidently_service(record, prediction):
    rec = record.copy()
    rec["prediction"] = prediction
    requests.post(
        f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/minifigure", json=rec, timeout=10
    )


def get_learner(model_run, tracking_server, tracking_server_port):
    """get model from mlflow model registry"""
    app.logger.info(
        "loading model from file %s and uri http://%s:%s" % (model_run, tracking_server, tracking_server_port)
    )

    mlflow.set_tracking_uri(f"http://{tracking_server}:80")
    app.logger.info(os.path.dirname(os.path.abspath(__file__)))
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


# get model from env
learn = get_learner(
    os.getenv("RUN_ID_STR", "runs:/5e8554e66b654f54ae52a7aeb9ff8b0d/model"),
    os.getenv("TRACKING_SERVER_HOST", "localhost"),
    os.getenv("TRACKING_SERVER_PORT", "80"),
)


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.route("/", methods=["GET"])
def get_info():
    """Function to provide info about the app"""
    # app.logger.info("get request")
    info = """<H1>Minifigure Prediction Service</H1>
              <div class="Data Request">
                <H3>Data Request Example</H3>
                <div class="data">
                <p> {
                    "index":0,
                    "path":"\/home\/ubuntu\/mlops_zoomcamp_homework\/data\/test\/001.jpg",
                    "class_id":32,
                    "minifigure_name":"JANNAH",
                    "labels":"jannah",
                    "fname":"\/home\/ubuntu\/mlops_zoomcamp_homework\/data\/test\/001.jpg"}
                </p>
                </div>
               </div>"""
    return info


@app.route("/predict", methods=["POST"])
def predict():
    print(request.get_json())
    request_dict = json.loads(request.get_json())
    del request_dict["index"]
    df_row = pd.read_json(json.dumps(request_dict), typ="series")
    app.logger.info(df_row.head())
    # return features
    y_pred, _ = make_single_prediction(df_row["path"])
    app.logger.info("Finished backend prediction")
    return_dict = {"y_pred": y_pred, "labels": df_row["class_id"]}
    app.logger.info(return_dict)

    save_to_db(request_dict, y_pred)
    logging.info("save to db")
    save_to_evidently_service(request_dict, y_pred)
    logging.info("save to evidently")

    #return_dict = {"y_pred": 9, "labels": 10}
    return jsonify(return_dict)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=9696)
