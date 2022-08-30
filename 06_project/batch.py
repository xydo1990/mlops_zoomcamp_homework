#!/usr/bin/env python
# coding: utf-8

### goal: predict new batch of data and store predictions to file for analysis
import pandas as pd
import numpy as np
import os
import argparse
from fastai.vision.all import *
from sklearn.metrics import accuracy_score


def store_predictions(df, y_pred, output_file, y=None):
    """ 
    stores predictions to output_file in parquet format 
    
    stores labels as well if present 
    """
    df_result = pd.DataFrame()
    df_result['fname'] = df['fname']
    df_result['y_pred'] = y_pred
    if y is not None:
        df_result['label'] = y

    dir_name = os.path.dirname(output_file)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    print(f"storing predictions to file {output_file}")
    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )
    print(f"size of saved data: {os.path.getsize(output_file) / 1000000}")


def preprocess_data(df, metadata):
    """ 
    add label column and change path to fname column

    need to have the same preprocessing steps as during training, number of features needs to stay the same 
    """
    df_lego = pd.merge(df, metadata['minifigure_name'], on='class_id')
    df_lego['labels'] = df_lego['minifigure_name'].apply(lambda x: x.lower())
    df_lego['fname'] = df_lego.path

    return df_lego


def get_data(data_path):
    """ gets data from path, loads it and returns data loader """
    print(f"loading data from file path: {data_path}")
    df = pd.read_csv(data_path, encoding = "utf8")
    lego_metadata = pd.read_csv(os.path.join(os.path.dirname(data_path), 'metadata.csv'), index_col=0)
    df_lego = preprocess_data(df, lego_metadata)
    # TODO use full df as validation, why not possible?
    dls_test = ImageDataLoaders.from_df(df_lego, Path(os.path.dirname(data_path)),
                                    item_tfms=Resize(412),
                                    bs=10, num_workers=0, label_col="labels", valid_pct=0)

    test_files = [os.path.join("data", str(fname)) for fname in list(df_lego["fname"])]     
    return dls_test, df_lego, test_files


def get_learner(model_path, dls):
    """ get model from mlflow model registry """
    # TODO make model architecture independent with pickle
    print(f"loading model from file {model_path}")
    learn = vision_learner(dls, 'resnet50', metrics=[error_rate, accuracy], model_dir=Path(os.path.dirname(model_path)),
                       path=Path(""
                                                                                                                    "."))
    learn.load(model_path)
    return learn


def make_predictions(learn, test_files):
    """ make predictions with data loader using learner """
    test_dl = learn.dls.test_dl(test_files)
    preds, _, decoded = learn.get_preds(dl=test_dl, with_decoded=True)
    y_pred = np.array([np.argmax(sample) for sample in preds])
    return y_pred, None


def calculate_metrics(y_pred, y):
    """ 
    calculate different metrics based on predictions 
    
    metrics are not stored atm 
    """
    accuracy = accuracy_score(y.numpy(), y_pred)
    print(f"accuracy {accuracy}")



def run(model_file, data_path, output_file):
    """ handles run of loading model and data, make predictions and store result """
    print("get data")
    dls, df_lego, test_files = get_data(data_path)
    print("get model")
    learner = get_learner(model_file, dls)
    print("make predictions")
    y_pred, y = make_predictions(learner, test_files)
    print("calculate metrics")
    if y is not None:
        calculate_metrics(y_pred, y)
    print("store predictions")
    store_predictions(df_lego, y_pred, output_file, y)

    # with open(model_path, 'rb') as f_in:
    #    dv, lr = pickle.load(f_in)
    

if __name__ == "__main__":
    # TODO store and load data from s3, as well as model
    # optional input arguments
    parser = argparse.ArgumentParser(description='prediction of values for production test')
    parser.add_argument('--data_path', type=str, help='path to csv of data to predict', 
        default="/home/ubuntu/mlops_zoomcamp_homework/06_project/data/test.csv")
    parser.add_argument('--model_file', type=str, help='path to model pth file, without.pth', 
        default="/home/ubuntu/mlops_zoomcamp_homework/06_project/models/resnet/model_best")
    parser.add_argument('--output_file', type=str, help='path of parquet file to store predictions', 
        default="/home/ubuntu/mlops_zoomcamp_homework/06_project/outputs/batch_predictions.parquet")
    args = parser.parse_args()

    run(args.model_file, args.data_path, args.output_file)

