# based on docker image with python 3.9 from homework 4
FROM agrigorev/zoomcamp-model:mlops-3.9.7-slim

RUN pip install -U pip
RUN pip install pipenv

WORKDIR /app

COPY [ "Pipfile", "Pipfile.lock", "./" ]

RUN pipenv install --system --deploy

COPY [ "06_project/batch.py", "batch.py" ]

ENTRYPOINT [ "python", "batch.py" ]