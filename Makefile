# export these two variables if calling publish

unittests:
	pytest tests/unittests.py

quality_checks:
	isort .
	black .
	pylint --rcfile=".pylintrc" ./src

# training with local tracking server
train:
	docker-compose -f src/docker-compose-train.yml up -d
	python src/train_model.py --tracking_server localhost
	docker-compose -f src/docker-compose-train.yml down

build: quality_checks unittests
	docker-compose build

integration_test: build
	chmod +x tests/integration_test.sh
	bash tests/integration_test.sh

publish: build integration_test
	docker login -u ${DOCKER_USER} -p ${DOCKER_PW}
	docker tag project_batch:latest xydo/zoomcamp-model:mlops_batch-0.1.0
	docker push xydo/zoomcamp-model:mlops_batch-0.1.0

publish_only:
	docker login -u ${DOCKER_USER} -p ${DOCKER_PW}
	docker tag project_batch:latest xydo/zoomcamp-model:mlops_batch-0.1.0
	docker push xydo/zoomcamp-model:mlops_batch-0.1.0

setup:
	pipenv install --dev
	pipenv shell
	pre-commit install
	cp sample.env .env

get_data:
	python src/get_data.py
