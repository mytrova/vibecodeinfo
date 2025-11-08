FROM python:3.11-alpine

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock .
RUN poetry install --no-root --with dev

COPY . .

CMD ["poetry", "run", "python3", "main.py"]


