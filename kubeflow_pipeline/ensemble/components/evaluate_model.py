from kfp.dsl import component, Input, Output, Dataset, Model, Metrics


@component(
    base_image="pod-placement-trainer:v11"
)
def evaluate_model(
    model: Input[Model],
    x_test: Input[Dataset],
    y_test: Input[Dataset],
    scenario_test: Input[Dataset],
    metrics: Output[Metrics],
):
    import joblib
    import pandas as pd
    from sklearn.metrics import mean_squared_error

    print("=" * 60)
    print("Loading model")
    print("=" * 60)

    rf = joblib.load(model.path)

    print("=" * 60)
    print("Loading test dataset")
    print("=" * 60)

    X_test = pd.read_csv(x_test.path)
    y_test_df = pd.read_csv(y_test.path)
    scenario_df = pd.read_csv(scenario_test.path)

    y_test = y_test_df["score"]
    scenario_ids = scenario_df["scenario_id"]

    print(f"Testing Samples : {len(X_test)}")

    print("=" * 60)
    print("Generating Predictions")
    print("=" * 60)

    predictions = rf.predict(X_test)

    print("=" * 60)
    print("Calculating RMSE")
    print("=" * 60)

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    results_df = pd.DataFrame({
        "scenario_id": scenario_ids,
        "true_score": y_test,
        "predicted_score": predictions,
    })

    print("=" * 60)
    print("Calculating Top-1 Agreement")
    print("=" * 60)

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

    top1_agreement = matches / len(true_best_rows)

    print("=" * 60)
    print("Evaluation Results")
    print("=" * 60)

    print(f"RMSE            : {rmse:.4f}")
    print(f"Top-1 Agreement : {top1_agreement:.4f}")

    metrics.log_metric("RMSE", float(rmse))
    metrics.log_metric("Top1_Agreement", float(top1_agreement))

    print("=" * 60)
    print("Metrics logged successfully")
    print("=" * 60)