from kfp.dsl import component, Input, Output, Dataset, Model


@component(
    base_image="pod-placement-trainer:v12"
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
        ExtraTreesRegressor,
        GradientBoostingRegressor,
        VotingRegressor,
    )
    from xgboost import XGBRegressor
    from catboost import CatBoostRegressor

    print("=" * 60)
    print("Loading training data")
    print("=" * 60)

    X_train = pd.read_csv(x_train.path)
    y_train = pd.read_csv(y_train.path)["score"]

    print(f"Training Samples : {len(X_train)}")
    print(f"Number of Features : {X_train.shape[1]}")

    print("=" * 60)
    print("Defining Base Estimators")
    print("=" * 60)

    rf = RandomForestRegressor(
        n_estimators=60,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )

    xgb = XGBRegressor(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
    )

    catboost = CatBoostRegressor(
        iterations=300,
        depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=False,
    )

    gbr = GradientBoostingRegressor(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )

    etr = ExtraTreesRegressor(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )

    print("=" * 60)
    print("Training Voting Regressor (RF + XGBoost + CatBoost + GBR + ExtraTrees)")
    print("=" * 60)

    voting_regressor = VotingRegressor(
        estimators=[
            ("random_forest", rf),
            ("xgboost", xgb),
            ("catboost", catboost),
            ("gradient_boosting", gbr),
            ("extra_trees", etr),
        ],
    )

    voting_regressor.fit(X_train, y_train)

    print("=" * 60)
    print("Extracting Fitted Base Models")
    print("=" * 60)

    # VotingRegressor clones + fits each estimator internally.
    # estimators_ holds the fitted clones in the same order as `estimators`.
    fitted_names = [name for name, _ in voting_regressor.estimators]
    fitted_models = dict(zip(fitted_names, voting_regressor.estimators_))

    model_bundle = {
        **fitted_models,
        "voting_regressor": voting_regressor,
    }

    print("=" * 60)
    print("Saving Model Bundle")
    print("=" * 60)

    joblib.dump(
        model_bundle,
        model.path,
        compress=3,
    )

    print(f"Model bundle saved at : {model.path}")
    print(f"Models in bundle : {list(model_bundle.keys())}")

    print("=" * 60)
    print("Training Completed")
    print("=" * 60)