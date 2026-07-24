FROM python:3.11-slim

WORKDIR /app

# System build dependencies needed by xgboost / catboost wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY components ./components
COPY pipeline.py .

CMD ["bash"]