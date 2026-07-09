from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


if not client.bucket_exists("datasets"):
    client.make_bucket("datasets")

if not client.bucket_exists("models"):
    client.make_bucket("models")



client.fput_object(
    "datasets",
    "dataset.csv",
    "../data/dataset.csv"
)

print("Dataset uploaded successfully")