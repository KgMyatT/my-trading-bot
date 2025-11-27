# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY . /app

# default command runs main with env args (override on docker run if needed)
CMD ["python", "main.py", "--csv", "/data/trades.csv", "--timeframe", "1min", "--gcs-bucket", ""]
