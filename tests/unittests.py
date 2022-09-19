import os
import unittest

import pandas as pd

from prediction_service_batch.batch_docker import preprocess_data, store_predictions


class TestBatchDocker(unittest.TestCase):
    @staticmethod
    def test_batch_data_preprocess():
        df = pd.DataFrame({"path": ["spider_1", "bee_2"], "class_id": [1, 0]})
        df_metadata = pd.DataFrame({"class_id": [0, 1], "lego_ids": ["lala", "blub"], "minifigure_name": ["Heinz", "Gerd"]})
        df_metadata = df_metadata.set_index("class_id")
        df_lego = preprocess_data(df, df_metadata)

        # check if columns were created as expected
        assert "fname" in df_lego.columns
        assert "labels" in df_lego.columns
        # check if merge with classnames was done
        assert "heinz" in list(df_lego["labels"])

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
