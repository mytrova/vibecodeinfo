-include .env
export

dev.install:
	poetry install --no-root --with dev --with lint --with tests

deps.lock:
	poetry lock

run:
	docker compose up --build

lint:
	flake8 vibecodeinfo tests
	mypy vibecodeinfo

test:
	pytest

db.init:
	docker compose run --rm vibecodeinfo python -m vibecodeinfo.db.init_db
