import os
import unittest

import pandas as pd
from src.batch_docker import get_data, store_predictions


class TestBatchDocker(unittest.TestCase):
    @staticmethod
    def test_batch_data_preprocess():
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "index.csv",
        )
        df = get_data(data_path)

        # check if columns were created as expected
        assert "fname" in df.columns
        assert "labels" in df.columns
        # check if merge with classnames was done
        assert "spider-man" in list(df["labels"])

    @staticmethod
    def test_batch_store_predictions():
        output_file = "tmp_test_predictions.parquet"
        df = pd.DataFrame()
        df["fname"] = ["test_1.png", "test_2.png"]
        y_pred = ["SPIDER-MAN", "HARRY_POTTER"]
        y = ["SPIDER-MAN", "SPIDER-MAN"]
        store_predictions(df, y_pred, output_file, y)

        assert os.path.exists(output_file)
        # reload stored file and verify content
        df_actual = pd.read_parquet(output_file)
        assert "label" in df_actual.columns


if __name__ == "__main__":
    unittest.main()
