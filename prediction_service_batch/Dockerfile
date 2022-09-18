FROM continuumio/miniconda3

WORKDIR /app

# conda environment for loading the model from file
COPY model/conda.yaml .
RUN conda update -n base -c defaults conda
RUN conda env create -f conda.yaml
RUN conda init bash
RUN echo "conda activate mlflow-env" > ~/.bashrc

# prepare code
COPY src/batch_docker.py .

# prepare aws connection


# The code to run when container is started:
SHELL ["conda", "run", "-n", "mlflow-env", "/bin/bash", "-c"]
ENTRYPOINT ["conda", "run", "-n", "mlflow-env", "python3", "batch_docker.py"]