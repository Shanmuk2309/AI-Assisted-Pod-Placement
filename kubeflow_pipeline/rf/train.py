import os
import json
import joblib
import pandas as pd

from minio import Minio

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


# =========================
# MINIO CLIENT
# =========================

client = Minio(
    "host.minikube.internal:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# =========================
# DOWNLOAD DATASET
# =========================

print("Downloading dataset from MinIO...")

client.fget_object(
    "datasets",
    "dataset.csv",
    "dataset.csv"
)

print("Dataset downloaded")

# =========================
# LOAD DATASET
# =========================

df = pd.read_csv(
    "dataset.csv"
)

print(df.columns.tolist())

print(f"Dataset rows: {len(df)}")

# =========================
# ENCODE CATEGORICALS
# =========================

difficulty_mapping = {
    "easy": 0,
    "medium": 1,
    "hard": 2
}

df["difficulty"] = df["difficulty"].map(
    difficulty_mapping
)

# =========================
# FEATURES
# =========================

features = [
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
    "du_mem_req"
]

X = df[features]

y = df["score"]


scenario_ids = df["scenario_id"]

X_train, X_test, y_train, y_test, scenario_train, scenario_test = train_test_split(
    X,
    y,
    scenario_ids,
    test_size=0.2,
    random_state=42
)

print(f"Train rows: {len(X_train)}")
print(f"Test rows: {len(X_test)}")


print("Training model...")

model = RandomForestRegressor(
    n_estimators=60,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)


model.fit(X_train, y_train)


print("Generating predictions...")

predictions = model.predict(X_test)


rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5

print(f"RMSE: {rmse:.4f}")



results_df = pd.DataFrame({
    "scenario_id": scenario_test.values,
    "true_score": y_test.values,
    "predicted_score": predictions
})

# Ground truth best placement
true_best = (
    results_df
    .groupby("scenario_id")["true_score"]
    .idxmax()
)

# Predicted best placement
pred_best = (
    results_df
    .groupby("scenario_id")["predicted_score"]
    .idxmax()
)

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

top1_agreement = matches / total

print(f"Top-1 Agreement: {top1_agreement:.4f}")


metrics = {
    "rmse": float(rmse),
    "top1_agreement": float(top1_agreement)
}

os.makedirs("/tmp", exist_ok=True)

with open("/tmp/metrics.json", "w") as f:
    json.dump(metrics, f)

print("Metrics saved")


os.makedirs("artifacts", exist_ok=True)

model_path = "artifacts/model.pkl"

joblib.dump(
    model,
    model_path,
    compress=3
)

print("Model saved locally")


client.fput_object(
    "models",
    "model.pkl",
    model_path
)

print("Model uploaded to MinIO")