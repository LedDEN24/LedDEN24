FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
       libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install ".[dev]"

COPY . /app

RUN python -m compileall estate_guard apps

CMD ["gunicorn", "estate_guard.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
