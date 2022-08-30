#!/usr/bin/env python
# coding: utf-8

### goal: predict new batch of data and store predictions to file for analysis
import pandas as pd
import numpy as np
import os
import argparse
from fastai.vision.all import *
from sklearn.metrics import accuracy_score


def make_predictions(df, categorical, dv, lr):
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print(f"mean prediction {np.mean(y_pred)}")
    return y_pred


def store_predictions(df, y_pred, year, month, output_file):
    # TODO enable storage of predictions
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    df['y_pred'] = y_pred

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['y_pred'] = df['y_pred']
    df_result.head()

    dir_name = os.path.dirname(output_file)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )
    print(f"size of saved data: {os.path.getsize(output_file) / 1000000}")


def run(model_path, data_path, output_path):
    """ handles run of loading model and data, make predictions and store result """
    print("get data")
    dls = get_data(args.data_path)
    print("get model")
    learner = get_learner(args.model_path, dls)
    print("make predictions")
    y_pred, y = make_predictions(learner, dls)
    print("calculate metrics")
    calculate_metrics(y_pred, y)
    #print("store predictions")
    #store_predictions(df, y_pred, year, month, output_file)

    #with open(model_path, 'rb') as f_in:
    #    dv, lr = pickle.load(f_in)
    #print("get files")
    #input_file, output_file = get_files(year, month)
    #print("read data")
    #df = read_data(input_file, categorical)
    #print("make predictions")
    #y_pred = make_predictions(df, categorical, dv, lr)
    #print("store predictions")
    #store_predictions(df, y_pred, year, month, output_file)


def preprocess_data(df, metadata):
    """ add label column and change path to fname column"""
    df_lego = pd.merge(df, metadata['minifigure_name'], on='class_id')
    df_lego['labels'] = df_lego['minifigure_name'].apply(lambda x: x.lower())
    df_lego['fname'] = df_lego['path']
    return df_lego


def get_data(data_path):
    """ gets data from path, loads it and returns data loader """
    df = pd.read_csv(data_path, index_col=1)
    lego_metadata = pd.read_csv(os.path.join(os.path.dirname(data_path), 'metadata.csv'), index_col=0)
    df_lego = preprocess_data(df, lego_metadata)
    dls_test = ImageDataLoaders.from_df(df_lego, os.path.dirname(data_path), valid_pct=1.0,
                                    item_tfms=Resize(412),
                                    bs=10, num_workers=0, label_col="labels")
    return dls_test


def get_learner(model_path, dls):
    """ get model from mlflow model registry """
    # TODO make model architecture independent
    learn = vision_learner(dls, 'resnet50', metrics=[error_rate, accuracy], model_dir = Path(os.path.dirname(model_path)),
                       path =Path(""
                                                                                                                    "."))
    learn.load(model_path)
    return learn


def make_predictions(learn, dls):
    """ make predictions with data loader using learner """
    preds, y = learn.get_preds(dl=dls.valid)
    y_pred = np.array([np.argmax(sample) for sample in preds])
    return y_pred, y


def calulate_metrics(y_pred, y):
    """ calculate different metrics based on predictions """
    accuracy = accuracy_score(y.numpy(), y_pred)
    print(f"best accuracy {accuracy}")
    


if __name__ == "__main__":
    # TODO store and load data from s3, as well as model
    parser = argparse.ArgumentParser(description='get this to production')
    parser.add_argument('data_path', type=int, help='path to csv of data to predict', default="~/mlops_zoomcamp_homework/06_project/data/test.csv")
    parser.add_argument('model_path', type=str, help='path to model', default="~/mlops_zoomcamp_homework/06_project/models/resnet/model_best.pth")
    parser.add_argument('output_path', type=str, help='path to store predictions', default="~/mlops_zoomcamp_homework/06_project/outputs/batch_predictions")
    args = parser.parse_args()

    run(args.data_path, args.model_path, args.output_path)

