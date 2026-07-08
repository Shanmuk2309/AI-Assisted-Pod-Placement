import io
import json
import joblib
import pandas as pd

from minio import Minio
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


# ==========================
# MinIO Configuration
# ==========================

MINIO_ENDPOINT = "host.minikube.internal:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

DATASET_BUCKET = "datasets"
MODEL_BUCKET = "models"
METRICS_BUCKET = "metrics"

DATASET_NAME = "dataset.csv"


# ==========================
# MinIO Client
# ==========================

def get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def ensure_bucket(client, bucket_name):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


# ==========================
# Dataset
# ==========================

def download_dataset(local_path="dataset.csv"):
    client = get_minio_client()

    client.fget_object(
        DATASET_BUCKET,
        DATASET_NAME,
        local_path
    )

    return pd.read_csv(local_path)


def preprocess(df):
    """
    Shared preprocessing for RF and XGB.
    """

    if "difficulty" in df.columns:
        mapping = {
            "easy": 0,
            "medium": 1,
            "hard": 2
        }

        df["difficulty"] = df["difficulty"].map(mapping)

    target = "score"

    feature_columns = [c for c in df.columns if c != target]

    X = df[feature_columns]

    y = df[target]

    return train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )


# ==========================
# Metrics
# ==========================

def calculate_rmse(model, X_test, y_test):

    pred = model.predict(X_test)

    return mean_squared_error(
        y_test,
        pred,
        squared=False
    )


def upload_metrics(metrics, filename):

    client = get_minio_client()

    ensure_bucket(client, METRICS_BUCKET)

    client.put_object(
        METRICS_BUCKET,
        filename,
        io.BytesIO(
            json.dumps(metrics, indent=4).encode()
        ),
        length=len(
            json.dumps(metrics).encode()
        ),
        content_type="application/json"
    )


# ==========================
# Models
# ==========================

def upload_model(model, filename):

    client = get_minio_client()

    ensure_bucket(client, MODEL_BUCKET)

    buffer = io.BytesIO()

    joblib.dump(model, buffer)

    buffer.seek(0)

    client.put_object(
        MODEL_BUCKET,
        filename,
        buffer,
        length=buffer.getbuffer().nbytes
    )


def download_model(filename):

    client = get_minio_client()

    response = client.get_object(
        MODEL_BUCKET,
        filename
    )

    data = io.BytesIO(response.read())

    return joblib.load(data)