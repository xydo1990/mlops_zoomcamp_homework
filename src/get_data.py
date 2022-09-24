import os

import kaggle


def get_data(data_path, download=False):
    """gets data from path, loads it and returns data loader"""
    if download:
        print(
            "download data from kaggle, assuming that you have"
            + "authentification key in correct ~/.kaggle/kaggle.json"
        )
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            "ihelon/lego-minifigures-classification",
            path=data_path,
            unzip=True,
        )
    else:
        print("use data copy from this repo")

    print(f"loading data from file path: {data_path}")


if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
    os.makedirs(data_path)
    get_data(data_path, download=True)
