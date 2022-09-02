from src.batch_docker import get_data, store_predictions
import pandas as pd
import numpy as np
import os
import unittest


class TestBatchDocker(unittest.TestCase):
    def test_batch_data_preprocess(self):
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "data", "index.csv")
        df = get_data(data_path)

        # check if columns were created as expected
        assert("fname" in df.columns, True)
        assert("labels" in df.columns, True)
        # check if merge with classnames was done
        assert("SPIDER-MAN" in list(df["labels"]), True)


    def test_batch_store_predictions(self):
        output_file = "tmp_test_predictions.parquet"
        df = pd.DataFrame()
        df['fname'] = ["test_1.png", "test_2.png"]
        y_pred = ["SPIDER-MAN", "HARRY_POTTER"]
        y = ["SPIDER-MAN", "SPIDER-MAN"]
        store_predictions(df, y_pred, output_file, y)

        assert(os.path.exists(output_file), True)
        # reload stored file and verify content
        df_actual = pd.read_parquet(output_file)
        assert("label" in df_actual.columns, True)


if __name__ == '__main__':
    unittest.main()