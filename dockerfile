FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN [ -f requirements.txt ] && pip install --no-cache-dir -r requirements.txt || true

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python3", "-u", "main.py"]