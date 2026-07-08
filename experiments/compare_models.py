import time
import os
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def calculate_top1_agreement(
    scenario_ids,
    true_scores,
    predicted_scores
):

    results_df = pd.DataFrame({

        "scenario_id": scenario_ids.values,

        "true_score": true_scores.values,

        "predicted_score": predicted_scores
    })

    true_best = (

        results_df

        .groupby("scenario_id")["true_score"]

        .idxmin()
    )

    pred_best = (

        results_df

        .groupby("scenario_id")["predicted_score"]

        .idxmin()
    )

    true_best_rows = results_df.loc[true_best]

    pred_best_rows = results_df.loc[pred_best]

    matches = 0

    total = len(true_best_rows)

    for scenario_id in true_best_rows["scenario_id"]:

        true_idx = (

            true_best_rows[
                true_best_rows["scenario_id"]
                == scenario_id
            ].index[0]
        )

        pred_idx = (

            pred_best_rows[
                pred_best_rows["scenario_id"]
                == scenario_id
            ].index[0]
        )

        if true_idx == pred_idx:
            matches += 1

    return matches / total


print("Loading dataset...")

df = pd.read_csv("../data/dataset.csv")

difficulty_mapping = {
    "easy": 0,
    "medium": 1,
    "hard": 2
}

df["difficulty"] = df["difficulty"].map(
    difficulty_mapping
)

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

(
    X_train,
    X_test,
    y_train,
    y_test,
    scenario_train,
    scenario_test

) = train_test_split(

    X,
    y,
    scenario_ids,

    test_size=0.2,
    random_state=42
)

print(f"Train rows: {len(X_train)}")
print(f"Test rows: {len(X_test)}")


# ==================================================
# RANDOM FOREST
# ==================================================

print("\nTraining Random Forest...")

start = time.time()

rf = RandomForestRegressor(
    n_estimators=60,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)

rf.fit(
    X_train,
    y_train
)

rf_train_time = time.time() - start

rf_preds = rf.predict(X_test)

rf_top1 = calculate_top1_agreement(
    scenario_test,
    y_test,
    rf_preds
)

rf_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        rf_preds
    )
)

joblib.dump(
    rf,
    "rf_model.pkl"
)

rf_size = (
    os.path.getsize(
        "rf_model.pkl"
    ) / 1024 / 1024
)


# ==================================================
# XGBOOST
# ==================================================

print("\nTraining XGBoost...")

start = time.time()

xgb = XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

xgb.fit(
    X_train,
    y_train
)

xgb_train_time = time.time() - start

xgb_preds = xgb.predict(X_test)

xgb_top1 = calculate_top1_agreement(
    scenario_test,
    y_test,
    xgb_preds
)

xgb_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        xgb_preds
    )
)

joblib.dump(
    xgb,
    "xgb_model.pkl"
)

xgb_size = (
    os.path.getsize(
        "xgb_model.pkl"
    ) / 1024 / 1024
)


# ==================================================
# INFERENCE BENCHMARK
# ==================================================

sample = X_test.iloc[:1000]

start = time.time()
rf.predict(sample)
rf_inference = time.time() - start

start = time.time()
xgb.predict(sample)
xgb_inference = time.time() - start


# ==================================================
# RESULTS
# ==================================================

results = pd.DataFrame([

    {
        "Model": "Random Forest",
        "RMSE": rf_rmse,
        "Top1 Agreement (%)": rf_top1 * 100,
        "Training Time (s)": rf_train_time,
        "Inference Time (s)": rf_inference,
        "Model Size (MB)": rf_size
    },

    {
        "Model": "XGBoost",
        "RMSE": xgb_rmse,
        "Top1 Agreement (%)": xgb_top1 * 100,
        "Training Time (s)": xgb_train_time,
        "Inference Time (s)": xgb_inference,
        "Model Size (MB)": xgb_size
    }

])

results.to_csv(
    "model_comparison.csv",
    index=False
)

print("\n========================")
print(results)
print("========================")

print("\nSaved:")
print(" - model_comparison.csv")
print(" - rf_model.pkl")
print(" - xgb_model.pkl")