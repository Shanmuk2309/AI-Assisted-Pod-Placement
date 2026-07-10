from kfp.dsl import component, Input, Output, Dataset, Model


@component(
    base_image="pod-placement-trainer:v11"
)
def train_model(
    x_train: Input[Dataset],
    y_train: Input[Dataset],
    model: Output[Model],
):
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor

    print("=" * 60)
    print("Loading training data")
    print("=" * 60)

    X_train = pd.read_csv(x_train.path)
    y_train = pd.read_csv(y_train.path)["score"]

    print(f"Training Samples : {len(X_train)}")
    print(f"Number of Features : {X_train.shape[1]}")

    print("=" * 60)
    print("Initializing Random Forest")
    print("=" * 60)

    rf = RandomForestRegressor(
        n_estimators=60,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )

    print("=" * 60)
    print("Training Model")
    print("=" * 60)

    rf.fit(X_train, y_train)

    print("=" * 60)
    print("Saving Model")
    print("=" * 60)

    joblib.dump(
        rf,
        model.path,
        compress=3,
    )

    print(f"Model saved at : {model.path}")

    print("=" * 60)
    print("Training Completed")
    print("=" * 60)