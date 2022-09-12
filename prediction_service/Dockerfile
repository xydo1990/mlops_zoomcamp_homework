FROM continuumio/miniconda3

WORKDIR /app

# conda environment for loading the model from file
COPY conda.yaml .
RUN conda update -n base -c defaults conda
RUN conda env create -f conda.yaml
RUN conda init bash
RUN echo "conda activate mlflow-env-stream" > ~/.bashrc

# prepare code
COPY app.py .

EXPOSE 9696

# The code to run when container is started:
SHELL ["conda", "run", "-n", "mlflow-env-stream", "/bin/bash", "-c"]
#ENTRYPOINT ["conda", "run", "-n", "mlflow-env-stream", "python3", "app.py"]
ENTRYPOINT ["conda", "run", "-n", "mlflow-env-stream", "gunicorn", "--bind=0.0.0.0:9696", "app:app"]
