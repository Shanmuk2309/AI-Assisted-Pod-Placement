from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "dataset"

# =========================
# DELETE ALL OBJECTS
# =========================

objects = client.list_objects(
    bucket_name,
    recursive=True
)

for obj in objects:

    client.remove_object(
        bucket_name,
        obj.object_name
    )

    print(f"Deleted object: {obj.object_name}")

# =========================
# DELETE BUCKET
# =========================

client.remove_bucket(bucket_name)

print(f"Deleted bucket: {bucket_name}")