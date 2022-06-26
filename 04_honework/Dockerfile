FROM agrigorev/zoomcamp-model:mlops-3.9.7-slim as base

FROM base AS python-deps
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
COPY ["starter.py", "/app"]
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

#FROM base AS runtime
#COPY --from=python-deps /.venv /.venv
#ENV PATH="/.venv/bin:$PATH"
#
## Create and switch to a new user
#RUN useradd --create-home appuser
#WORKDIR /app
#USER appuser
#
#COPY ["starter.py", "/app"]
