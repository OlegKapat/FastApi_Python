FROM python:3.12-slim

WORKDIR /app

ENV POETRY_NO_INTERACTION=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-ansi --no-interaction --no-root

COPY app /app
EXPOSE 12321
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12321", "--reload"]
