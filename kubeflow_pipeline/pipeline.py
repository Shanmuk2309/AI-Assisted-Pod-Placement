from kfp import compiler
from kfp import dsl
from kfp.dsl import InputPath
from kfp.dsl import OutputPath


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def download_dataset(dataset_csv: OutputPath(str)):
    import os

    from minio import Minio

    endpoint = os.getenv("MINIO_ENDPOINT", "host.minikube.internal:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    bucket = os.getenv("DATASET_BUCKET", "datasets")
    object_name = os.getenv("DATASET_OBJECT", "dataset.csv")

    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )

    client.fget_object(bucket, object_name, dataset_csv)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def split_dataset(
    dataset_csv: InputPath(str),
    train_csv: OutputPath(str),
    test_csv: OutputPath(str),
):
    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(dataset_csv)

    if "difficulty" in df.columns:
        df = df.copy()
        df["difficulty"] = df["difficulty"].map(
            {
                "easy": 0,
                "medium": 1,
                "hard": 2,
            }
        )

    required_columns = [
        "difficulty",
        "cu_cpu_free_ratio",
        "du_cpu_free_ratio",
        "cu_mem_free_ratio",
        "du_mem_free_ratio",
        "latency_ms",
        "latency_budget",
        "same_node",
        "same_zone",
        "cu_load",
        "du_load",
        "cu_cpu_violation",
        "cu_mem_violation",
        "du_cpu_violation",
        "du_mem_violation",
        "cpu_balance",
        "mem_balance",
        "cu_cpu_req",
        "du_cpu_req",
        "cu_mem_req",
        "du_mem_req",
        "score",
        "scenario_id",
    ]

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
    )

    train_df.to_csv(train_csv, index=False)
    test_df.to_csv(test_csv, index=False)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def train_random_forest(train_csv: InputPath(str), rf_model: OutputPath(str)):
    import pandas as pd
    from joblib import dump
    from sklearn.ensemble import RandomForestRegressor

    df = pd.read_csv(train_csv)

    feature_columns = [
        "difficulty",
        "cu_cpu_free_ratio",
        "du_cpu_free_ratio",
        "cu_mem_free_ratio",
        "du_mem_free_ratio",
        "latency_ms",
        "latency_budget",
        "same_node",
        "same_zone",
        "cu_load",
        "du_load",
        "cu_cpu_violation",
        "cu_mem_violation",
        "du_cpu_violation",
        "du_mem_violation",
        "cpu_balance",
        "mem_balance",
        "cu_cpu_req",
        "du_cpu_req",
        "cu_mem_req",
        "du_mem_req",
    ]

    X_train = df[feature_columns]
    y_train = df["score"]

    model = RandomForestRegressor(
        n_estimators=60,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    dump(model, rf_model)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def train_xgboost(train_csv: InputPath(str), xgb_model: OutputPath(str)):
    import pandas as pd
    from joblib import dump
    from xgboost import XGBRegressor

    df = pd.read_csv(train_csv)

    feature_columns = [
        "difficulty",
        "cu_cpu_free_ratio",
        "du_cpu_free_ratio",
        "cu_mem_free_ratio",
        "du_mem_free_ratio",
        "latency_ms",
        "latency_budget",
        "same_node",
        "same_zone",
        "cu_load",
        "du_load",
        "cu_cpu_violation",
        "cu_mem_violation",
        "du_cpu_violation",
        "du_mem_violation",
        "cpu_balance",
        "mem_balance",
        "cu_cpu_req",
        "du_cpu_req",
        "cu_mem_req",
        "du_mem_req",
    ]

    X_train = df[feature_columns]
    y_train = df["score"]

    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    dump(model, xgb_model)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def build_ensemble_bundle(
    rf_model: InputPath(str),
    xgb_model: InputPath(str),
    ensemble_bundle: OutputPath(str),
):
    import json

    from joblib import dump, load

    rf = load(rf_model)
    xgb = load(xgb_model)

    bundle = {
        "strategy": "mean",
        "models": {
            "random_forest": rf,
            "xgboost": xgb,
        },
        "metadata": {
            "description": "Averaging ensemble of RandomForestRegressor and XGBRegressor",
        },
    }

    dump(bundle, ensemble_bundle)

    with open(ensemble_bundle + ".json", "w", encoding="utf-8") as metadata_file:
        json.dump(bundle["metadata"], metadata_file, indent=2)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def upload_ensemble_bundle(ensemble_bundle: InputPath(str)):
    import os

    from minio import Minio

    endpoint = os.getenv("MINIO_ENDPOINT", "host.minikube.internal:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    bucket = os.getenv("MODEL_BUCKET", "models")
    object_name = os.getenv("ENSEMBLE_OBJECT", "ensemble_model.pkl")

    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )

    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    client.fput_object(bucket, object_name, ensemble_bundle)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def evaluate_ensemble(
    ensemble_bundle: InputPath(str),
    test_csv: InputPath(str),
    metrics_json: OutputPath(str),
):
    import json

    import numpy as np
    import pandas as pd
    from joblib import load
    from sklearn.metrics import mean_squared_error

    df = pd.read_csv(test_csv)

    feature_columns = [
        "difficulty",
        "cu_cpu_free_ratio",
        "du_cpu_free_ratio",
        "cu_mem_free_ratio",
        "du_mem_free_ratio",
        "latency_ms",
        "latency_budget",
        "same_node",
        "same_zone",
        "cu_load",
        "du_load",
        "cu_cpu_violation",
        "cu_mem_violation",
        "du_cpu_violation",
        "du_mem_violation",
        "cpu_balance",
        "mem_balance",
        "cu_cpu_req",
        "du_cpu_req",
        "cu_mem_req",
        "du_mem_req",
    ]

    X_test = df[feature_columns]
    y_test = df["score"]
    scenario_ids = df["scenario_id"]

    bundle = load(ensemble_bundle)
    rf = bundle["models"]["random_forest"]
    xgb = bundle["models"]["xgboost"]

    rf_predictions = rf.predict(X_test)
    xgb_predictions = xgb.predict(X_test)
    ensemble_predictions = np.mean(
        np.vstack([rf_predictions, xgb_predictions]),
        axis=0,
    )

    rmse = mean_squared_error(y_test, ensemble_predictions, squared=False)

    results_df = pd.DataFrame(
        {
            "scenario_id": scenario_ids.values,
            "true_score": y_test.values,
            "predicted_score": ensemble_predictions,
        }
    )

    true_best = results_df.groupby("scenario_id")["true_score"].idxmin()
    pred_best = results_df.groupby("scenario_id")["predicted_score"].idxmin()

    true_best_rows = results_df.loc[true_best]
    pred_best_rows = results_df.loc[pred_best]

    matches = 0
    total = len(true_best_rows)

    for scenario_id in true_best_rows["scenario_id"]:
        true_idx = true_best_rows[
            true_best_rows["scenario_id"] == scenario_id
        ].index[0]
        pred_idx = pred_best_rows[
            pred_best_rows["scenario_id"] == scenario_id
        ].index[0]

        if true_idx == pred_idx:
            matches += 1

    top1_agreement = matches / total if total else 0.0

    metrics = {
        "rmse": float(rmse),
        "top1_agreement": float(top1_agreement),
    }

    with open(metrics_json, "w", encoding="utf-8") as output_file:
        json.dump(metrics, output_file, indent=2)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "joblib",
        "minio",
        "numpy",
        "pandas",
        "scikit-learn",
        "xgboost",
    ],
)
def report_metrics(metrics_json: InputPath(str)):
    import json

    with open(metrics_json, "r", encoding="utf-8") as input_file:
        metrics = json.load(input_file)

    print("Ensemble metrics")
    print(f"RMSE: {metrics['rmse']:.4f}")
    print(f"Top-1 Agreement: {metrics['top1_agreement']:.4f}")


@dsl.pipeline(name="Pod Placement Ensemble Pipeline")
def pod_pipeline():
    dataset_task = download_dataset()
    split_task = split_dataset(dataset_csv=dataset_task.outputs["dataset_csv"])

    rf_task = train_random_forest(train_csv=split_task.outputs["train_csv"])
    xgb_task = train_xgboost(train_csv=split_task.outputs["train_csv"])

    ensemble_task = build_ensemble_bundle(
        rf_model=rf_task.outputs["rf_model"],
        xgb_model=xgb_task.outputs["xgb_model"],
    )

    upload_task = upload_ensemble_bundle(
        ensemble_bundle=ensemble_task.outputs["ensemble_bundle"]
    )

    metrics_task = evaluate_ensemble(
        ensemble_bundle=ensemble_task.outputs["ensemble_bundle"],
        test_csv=split_task.outputs["test_csv"],
    ).after(upload_task)

    report_metrics(metrics_json=metrics_task.outputs["metrics_json"]).after(metrics_task)


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=pod_pipeline,
        package_path="pipeline.yaml",
    )