run:
	docker build -t vibecodeinfo .
	docker run --env-file .env vibecodeinfo

mypy:
	docker build -t vibecodeinfo .
	docker run --rm vibecodeinfo poetry run mypy .



flake8:
	docker build -t vibecodeinfo .
	docker run --rm vibecodeinfo poetry run flake8 .
