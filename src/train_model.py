import argparse
import os
import random

import numpy as np
import pandas as pd
import timm
import torch
from fastai.vision.all import *
from fastai.vision.learner import _update_first_layer
from sklearn.metrics import accuracy_score

import mlflow


def seed_everything(seed=0):
    """ensure reproducability by defining random seed"""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def preprocess_data(df, metadata):
    """add label column and change path to fname column"""
    df_lego = pd.merge(df, metadata["minifigure_name"], on="class_id")
    df_lego["labels"] = df_lego["minifigure_name"].apply(lambda x: x.lower())
    df_lego["fname"] = df_lego["path"]
    return df_lego


def data_preprocess_handler(path):
    df = pd.read_csv(os.path.join(path, "index.csv"), index_col=1)
    lego_metadata = pd.read_csv(os.path.join(path, "metadata.csv"), index_col=0)
    df_lego = preprocess_data(df, lego_metadata)
    data = ImageDataLoaders.from_df(
        df_lego,
        path,
        valid_pct=0.10,
        item_tfms=Resize(412),
        bs=10,
        num_workers=0,
        label_col="labels",
    )
    return data


def create_timm_body(arch: str, pretrained=True, cut=None, n_in=3):
    "Creates a body from any model in the `timm` library."
    model = timm.create_model(
        arch, pretrained=pretrained, num_classes=0, global_pool=""
    )
    _update_first_layer(model, n_in, pretrained)
    if cut is None:
        ll = list(enumerate(model.children()))
        cut = next(i for i, o in reversed(ll) if has_pool_type(o))
    if isinstance(cut, int):
        return nn.Sequential(*list(model.children())[:cut])
    elif callable(cut):
        return cut(model)
    else:
        raise timm.NamedError("cut must be either integer or function")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="training an image classifier and tracking experiment with mlflow"
    )
    parser.add_argument(
        "--tracking_server",
        type=str,
        help="mlflow tracking server host",
        default="localhost",
    )
    parser.add_argument(
        "--n_cores",
        type=int,
        help="number of cpu cores",
        default=1,
    )
    parser.add_argument(
        "--data_path",
        type=str,
        help="path to minifigure data folder relative to this file",
        default="../data",
    )
    args = parser.parse_args()

    seed_everything()

    os.environ["AWS_PROFILE"] = "default"  # fill in with your AWS profile.
    # fill in with the public DNS of the EC2 instance
    TRACKING_SERVER_HOST = os.getenv("TRACKING_SERVER_HOST", args.tracking_server)
    mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
    os.environ["TORCH_HOME"] = "models\\resnet"  # setting the environment variable
    # path to downloaded dataset
    path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), args.data_path
    )  
    torch.set_num_threads(args.n_cores)  # adapt to your hardware setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    mlflow.set_experiment("project_resnet50_v1")

    mlflow.fastai.autolog()

    with mlflow.start_run():
        data = data_preprocess_handler(path)

        params = {"lr1": 1e-3, "lr2": 1e-1, "random_seed": 0, "model": "resnet50"}
        mlflow.log_params(params)

        learn = vision_learner(
            data,
            "resnet50",
            metrics=[error_rate, accuracy],
            model_dir=Path(os.path.join(os.getcwd(), "models", "resnet")),
            path=Path("" "."),
        )
        # SaveModelCallback loads best model at the end of training
        learn.fit_one_cycle(
            100,
            slice(params["lr1"], params["lr2"]),
            cbs=[
                EarlyStoppingCallback(patience=2),
                SaveModelCallback(fname="model_best"),
                ReduceLROnPlateau(),
            ],
        )

        preds, y = learn.get_preds(dl=data.valid)
        y_hat = np.array([np.argmax(sample) for sample in preds])
        accuracy_best = accuracy_score(y.numpy(), y_hat)
        print(f"best accuracy {accuracy_best}")
        mlflow.log_metric("accuracy_best", accuracy_best)

        # manually load best model (if not trained)
        learn_best = vision_learner(
            data,
            "resnet50",
            metrics=[error_rate, accuracy],
            model_dir=Path(os.path.join(os.getcwd(), "models", "resnet")),
            path=Path("" "."),
        )

        best_model_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "models",
            "resnet",
            "model_best",
        )
        print(best_model_path)
        learn_best.load(best_model_path)
        print(f"number classes {data.c}")
        preds, y = learn_best.get_preds(dl=data.valid)
        y_hat = np.array([np.argmax(sample) for sample in preds])
        accuracy_best = accuracy_score(y.numpy(), y_hat)
        print(f"best accuracy {accuracy_best}")
