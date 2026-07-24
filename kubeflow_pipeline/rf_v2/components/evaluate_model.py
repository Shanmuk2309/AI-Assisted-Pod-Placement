from kfp.dsl import component, Input, Output, Dataset, Model, Metrics


@component(
    base_image="pod-placement-trainer:v12"
)
def evaluate_model(
    model: Input[Model],
    x_test: Input[Dataset],
    y_test: Input[Dataset],
    scenario_test: Input[Dataset],
    metrics: Output[Metrics],
    metrics_csv: Output[Dataset],
):
    import joblib
    import pandas as pd
    from sklearn.metrics import mean_squared_error, mean_absolute_error

    def compute_top1_agreement(results_df):
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
        for scenario_id in true_best_rows["scenario_id"]:
            true_index = true_best_rows[
                true_best_rows["scenario_id"] == scenario_id
            ].index[0]
            pred_index = pred_best_rows[
                pred_best_rows["scenario_id"] == scenario_id
            ].index[0]
            if true_index == pred_index:
                matches += 1

        return matches / len(true_best_rows)

    def compute_all_metrics(y_true, y_pred, scenario_ids):
        rmse = mean_squared_error(y_true, y_pred) ** 0.5
        mae = mean_absolute_error(y_true, y_pred)

        results_df = pd.DataFrame({
            "scenario_id": scenario_ids,
            "true_score": y_true,
            "predicted_score": y_pred,
        })
        top1 = compute_top1_agreement(results_df)

        return rmse, mae, top1

    print("=" * 60)
    print("Loading model bundle")
    print("=" * 60)

    trained_models = joblib.load(model.path)

    print("=" * 60)
    print("Loading test dataset")
    print("=" * 60)

    X_test = pd.read_csv(x_test.path)
    y_test_df = pd.read_csv(y_test.path)
    scenario_df = pd.read_csv(scenario_test.path)

    y_true = y_test_df["score"]
    scenario_ids = scenario_df["scenario_id"]

    print(f"Testing Samples : {len(X_test)}")

    print("=" * 60)
    print("Generating Predictions")
    print("=" * 60)

    predictions = {}
    for name, mdl in trained_models.items():
        predictions[name] = mdl.predict(X_test)

    print("=" * 60)
    print("Calculating Metrics Per Model")
    print("=" * 60)

    rows = []
    for name, preds in predictions.items():
        rmse, mae, top1 = compute_all_metrics(y_true, preds, scenario_ids)
        rows.append({
            "model": name,
            "rmse": rmse,
            "mae": mae,
            "top1_agreement": top1,
        })

        print(f"[{name}] RMSE: {rmse:.4f} | MAE: {mae:.4f} | Top-1: {top1:.4f}")

    metrics_df = pd.DataFrame(rows)

    print("=" * 60)
    print("Saving Metrics CSV")
    print("=" * 60)

    metrics_df.to_csv(metrics_csv.path, index=False)

    print(f"Metrics CSV saved at : {metrics_csv.path}")

    print("=" * 60)
    print("Logging Voting Regressor Metrics")
    print("=" * 60)

    voting_row = metrics_df[metrics_df["model"] == "voting_regressor"].iloc[0]
    metrics.log_metric("RMSE", float(voting_row["rmse"]))
    metrics.log_metric("MAE", float(voting_row["mae"]))
    metrics.log_metric("Top1_Agreement", float(voting_row["top1_agreement"]))

    print("=" * 60)
    print("Evaluation Completed")
    print("=" * 60)