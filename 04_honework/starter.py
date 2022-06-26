#!/usr/bin/env python
# coding: utf-8

import pickle
import pandas as pd
import numpy as np
import os
import argparse

categorical = ['PUlocationID', 'DOlocationID']


def read_data(filename, categorical):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df


def make_predictions(df, categorical, dv, lr):
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)
    print(f"mean prediction {np.mean(y_pred)}")
    return y_pred


def store_predictions(df, y_pred, year, month, output_file):
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


def get_files(year, month):
    print(f"year {year}")
    print(f"month {month}")
    input_file = f'https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f"./output/predictions_year={year}_month={month}.parquet"
    return input_file, output_file


def run(year, month, model_path):
    with open(model_path, 'rb') as f_in:
        dv, lr = pickle.load(f_in)
    print("get files")
    input_file, output_file = get_files(year, month)
    print("read data")
    df = read_data(input_file, categorical)
    print("make predictions")
    y_pred = make_predictions(df, categorical, dv, lr)
    print("store predictions")
    store_predictions(df, y_pred, year, month, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='get this to production')
    parser.add_argument('year', type=int, help='year of data')
    parser.add_argument('month', type=int, help='month of data')
    parser.add_argument('model_path', type=str, help='path to model', default="model.bin")
    args = parser.parse_args()
    run(args.year, args.month, args.model_path)

