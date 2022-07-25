import pandas as pd
from datetime import datetime
import os
from homework_six.src.batch import read_data


def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)


def test_store_to_s3():
    """ write dataframe to local s3 storage """
    options = {
        'client_kwargs': {
            'endpoint_url': str(os.getenv("S3_ENDPOINT_URL", "http://localhost:4566"))
        }
    }
    year = 2021
    month = 1
    input_file = f"s3://nyc-duration/in/fhv_tripdata_{year:04d}-{month:02d}.parquet"
    print(f"storing to file {input_file}")

    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (1, 1, dt(1, 2, 0), dt(2, 2, 1)),
    ]
    columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
    df_input = pd.DataFrame(data, columns=columns)

    df_input.to_parquet(
        input_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options
    )
    # test if file is present
    categorical = ['PUlocationID', 'DOlocationID']
    # if runs, file is present and can be loaded, no assert needed
    read_data(input_file, categorical)
    print("file can be loaded from s3")
    # assert(True, True)


if "__name__" == "__main__":
    test_store_to_s3()