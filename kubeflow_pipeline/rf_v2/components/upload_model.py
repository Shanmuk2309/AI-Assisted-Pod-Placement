from kfp.dsl import component, Input, Model


@component(
    base_image="pod-placement-trainer:v12"
)
def upload_model(
    model: Input[Model],
):
    import joblib
    import tempfile
    import os
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

    bucket_name = "models"

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")

    print("=" * 60)
    print("Loading model bundle")
    print("=" * 60)

    trained_models = joblib.load(model.path)

    with tempfile.TemporaryDirectory() as tmp_dir:

        print("=" * 60)
        print("Uploading Voting Regressor as model.pkl")
        print("=" * 60)

        voting_regressor = trained_models["voting_regressor"]
        main_path = os.path.join(tmp_dir, "model.pkl")
        joblib.dump(voting_regressor, main_path, compress=3)

        client.fput_object(
            bucket_name=bucket_name,
            object_name="model.pkl",
            file_path=main_path,
        )
        print("Uploaded : model.pkl (voting_regressor)")

        print("=" * 60)
        print("Uploading Individual Base Models")
        print("=" * 60)

        for name, mdl in trained_models.items():
            if name == "voting_regressor":
                continue

            object_name = f"{name}.pkl"
            tmp_path = os.path.join(tmp_dir, object_name)

            joblib.dump(mdl, tmp_path, compress=3)

            client.fput_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=tmp_path,
            )
            print(f"Uploaded : {object_name}")

    print("=" * 60)
    print("Upload Completed")
    print("=" * 60)

    print(f"Bucket : {bucket_name}")
    print(f"Base models uploaded : {[n for n in trained_models if n != 'voting_regressor']}")