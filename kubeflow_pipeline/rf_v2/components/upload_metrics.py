from kfp.dsl import component, Input, Dataset


@component(
    base_image="pod-placement-trainer:v12"
)
def upload_metrics(
    metrics_csv: Input[Dataset],
):
    from minio import Minio

    print("=" * 60)
    print("Connecting to MinIO")
    print("=" * 60)

    client = Minio(
        "host.minikube.internal:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )

    bucket_name = "metrics"
    object_name = "model_metrics.csv"

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")

    print("=" * 60)
    print("Uploading Metrics CSV")
    print("=" * 60)

    client.fput_object(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=metrics_csv.path,
    )

    print("=" * 60)
    print("Upload Completed")
    print("=" * 60)

    print(f"Bucket : {bucket_name}")
    print(f"Object : {object_name}")