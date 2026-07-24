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

    from sklearn.ensemble import (
        RandomForestRegressor,
        AdaBoostRegressor,
        VotingRegressor,
    )

    from xgboost import XGBRegressor
    from catboost import CatBoostRegressor


    # ==========================================================
    # Load Training Data
    # ==========================================================

    print("=" * 60)
    print("Loading Training Data")
    print("=" * 60)

    X_train = pd.read_csv(x_train.path)
    y_train_df = pd.read_csv(y_train.path)

    y_train_values = y_train_df["score"]

    print(f"Training Samples   : {len(X_train)}")
    print(f"Number of Features : {X_train.shape[1]}")


    # ==========================================================
    # Random Forest
    # ==========================================================

    print("=" * 60)
    print("Initializing Random Forest")
    print("=" * 60)

    random_forest = RandomForestRegressor(
        n_estimators=60,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )


    # ==========================================================
    # XGBoost
    # ==========================================================

    print("=" * 60)
    print("Initializing XGBoost")
    print("=" * 60)

    xgboost = XGBRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
        objective="reg:squarederror",
    )


    # ==========================================================
    # CatBoost
    # ==========================================================

    print("=" * 60)
    print("Initializing CatBoost")
    print("=" * 60)

    catboost = CatBoostRegressor(
        iterations=100,
        depth=8,
        learning_rate=0.1,
        random_seed=42,
        verbose=False,
        thread_count=-1,
    )


    # ==========================================================
    # AdaBoost
    # ==========================================================

    print("=" * 60)
    print("Initializing AdaBoost")
    print("=" * 60)

    adaboost = AdaBoostRegressor(
        n_estimators=100,
        learning_rate=0.1,
        random_state=42,
    )


    # ==========================================================
    # Voting Regressor
    # ==========================================================

    print("=" * 60)
    print("Creating Voting Regressor")
    print("=" * 60)

    voting_regressor = VotingRegressor(
        estimators=[
            ("random_forest", random_forest),
            ("xgboost", xgboost),
            ("catboost", catboost),
            ("adaboost", adaboost),
        ],
        n_jobs=-1,
    )


    # ==========================================================
    # Train Ensemble
    # ==========================================================

    print("=" * 60)
    print("Training Voting Regressor Ensemble")
    print("=" * 60)

    voting_regressor.fit(
        X_train,
        y_train_values,
    )


    # ==========================================================
    # Save Ensemble Model
    # ==========================================================

    print("=" * 60)
    print("Saving Ensemble Model")
    print("=" * 60)

    joblib.dump(
        voting_regressor,
        model.path,
        compress=3,
    )

    print(f"Ensemble model saved at: {model.path}")

    print("=" * 60)
    print("Ensemble Training Completed")
    print("=" * 60)