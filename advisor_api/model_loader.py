import os
import joblib

from minio import Minio

MODEL_PATH = "model.pkl"

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)


def load_model():

    if not os.path.exists(MODEL_PATH):

        print("Downloading model from MinIO...")

        client.fget_object(
            "models",
            "model.pkl",
            MODEL_PATH
        )

        print("Model downloaded")

    return joblib.load(MODEL_PATH)