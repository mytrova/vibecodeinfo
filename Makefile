-include .env
export

dev.install:
	poetry install --no-root --with dev --with lint --with tests

deps.lock:
	poetry lock

run:
	python -m vibecodeinfo

docker.run:
	docker build -t vibecodeinfo .
	docker run --env-file .env vibecodeinfo

lint:
	flake8 vibecodeinfo tests
	mypy vibecodeinfo

test:
	pytest
