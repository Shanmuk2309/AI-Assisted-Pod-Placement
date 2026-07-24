from kfp.dsl import component, Output, Dataset

@component(
    base_image="pod-placement-trainer:v11"
)
def load_dataset(
    dataset: Output[Dataset]
):
    from minio import Minio
    import os

    print("=" * 60)
    print("Loading dataset from MinIO")
    print("=" * 60)

    client = Minio(
        "host.minikube.internal:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )

    os.makedirs(os.path.dirname(dataset.path), exist_ok=True)

    client.fget_object(
        bucket_name="datasets",
        object_name="dataset.csv",
        file_path=dataset.path,
    )

    print(f"Dataset saved to: {dataset.path}")