from homework_six.src.batch import prepare_data
import pandas as pd
from datetime import datetime


def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)


def test_batch():
    categorical = ['PUlocationID', 'DOlocationID']
    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (1, 1, dt(1, 2, 0), dt(2, 2, 1)),
    ]
    columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
    df_actual = pd.DataFrame(data, columns=columns)

    df_actual = prepare_data(df_actual, categorical)

    data_expected = [
        ("-1", "-1", dt(1, 2), dt(1, 10), 8.0),
        (1, 1, dt(1, 2), dt(1, 10), 8.0),
    ]
    columns_expected = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime', 'duration']
    df_expected = pd.DataFrame(data_expected, columns=columns_expected)
    # print(df_actual.compare(df_expected))

    assert(df_actual, df_expected)