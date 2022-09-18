import os
import unittest

import pandas as pd


class TestIntegrationBatchDocker(unittest.TestCase):
    @staticmethod
    def test_batch_integration():
        """runs full cycle of batch prediction
        including check if predictions are stored

        integration_test.sh file is used to setup environment
        as in real production via docker-compose file"""
        output_file = (
            "s3://" + os.getenv("MLFLOW_BUCKET_NAME") + "/batch_prediction.parquet"
        )
        df = pd.read_parquet(output_file)
        # TODO improve this test with content checks
        assert df is not None


if __name__ == "__main__":
    unittest.main()
