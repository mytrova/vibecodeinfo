FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry==2.2.1 poetry-plugin-export==1.9.0
COPY pyproject.toml poetry.lock .
RUN poetry export -o requirements.txt && pip install -r requirements.txt

COPY Makefile /app/
COPY vibecodeinfo /app/vibecodeЖinfo

CMD ["python3", "vibecodeinfo/__main__.py"]


