#!/usr/bin/env python
# coding: utf-8

import sys
import pickle
import pandas as pd
import os


def get_input_path(year, month):
    # default_input_pattern = 'https://raw.githubusercontent.com/alexeygrigorev/datasets/master/nyc-tlc/fhv/fhv_tripdata_{year:04d}-{month:02d}.parquet'
    default_input_pattern = "s3://nyc-duration/in/fhv_tripdata_{year:04d}-{month:02d}.parquet"
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year, month):
    default_output_pattern = 's3://nyc-duration/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)


def prepare_data(df, categorical):
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df


def save_data(dataframe, input_file):
    options = {
        'client_kwargs': {
            'endpoint_url': str(os.getenv("S3_ENDPOINT_URL", 'http://localhost:4566'))
        }
    }
    dataframe.to_parquet(
        input_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
    )


def read_data(filename, categorical):
    print(f"read filename {filename}")
    if os.getenv("S3_ENDPOINT_URL", 'http://localhost:4566') is not None:
        print(f"S3 entrypoint is {os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')}")
        options = {
            'client_kwargs': {
                'endpoint_url': str(os.getenv("S3_ENDPOINT_URL", 'http://localhost:4566'))
            }
        }
        print("read from localstack S3")
        df = pd.read_parquet(filename, storage_options=options)
    else:
        print("read from tutorial external s3")
        df = pd.read_parquet(filename)

    df = prepare_data(df, categorical)
    return df


def main(year, month):
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)
    # input_file = f'https://raw.githubusercontent.com/alexeygrigorev/datasets/master/nyc-tlc/fhv/fhv_tripdata_{year:04d}-{month:02d}.parquet'
    # # output_file = f's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    # output_file = f'taxi_type=fhv_year={year:04d}_month={month:02d}.parquet'

    print("loading model")
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    categorical = ['PUlocationID', 'DOlocationID']

    print("reading data")
    df = read_data(input_file, categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean())
    print('predicted mean duration:', y_pred.sum())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    df_result.to_parquet(output_file, engine='pyarrow', index=False)


if __name__ == "__main__":
    year = int(sys.argv[1])
    month = int(sys.argv[2])

    main(year, month)
