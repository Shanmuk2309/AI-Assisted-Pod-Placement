from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# =========================
# CREATE BUCKETS
# =========================

if not client.bucket_exists("datasets"):
    client.make_bucket("datasets")

if not client.bucket_exists("models"):
    client.make_bucket("models")

# =========================
# UPLOAD DATASET
# =========================

client.fput_object(
    "datasets",
    "dataset_small.csv",
    "../data/dataset_small.csv"
)

print("Dataset uploaded successfully")