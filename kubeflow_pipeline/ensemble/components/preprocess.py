from kfp.dsl import component, Input, Output, Dataset


@component(
    base_image="pod-placement-trainer:v11"
)
def preprocess(
    dataset: Input[Dataset],
    x_train: Output[Dataset],
    x_test: Output[Dataset],
    y_train: Output[Dataset],
    y_test: Output[Dataset],
    scenario_test: Output[Dataset],
):
    import pandas as pd
    from sklearn.model_selection import train_test_split

    print("=" * 60)
    print("Loading dataset")
    print("=" * 60)

    df = pd.read_csv(dataset.path)

    print(f"Dataset Shape : {df.shape}")

    print("=" * 60)
    print("Encoding categorical features")
    print("=" * 60)

    difficulty_mapping = {
        "easy": 0,
        "medium": 1,
        "hard": 2,
    }

    df["difficulty"] = df["difficulty"].map(difficulty_mapping)

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
        "du_mem_req",
    ]

    X = df[features]
    y = df["score"]
    scenario_ids = df["scenario_id"]

    (
        X_train,
        X_test,
        y_train_df,
        y_test_df,
        _,
        scenario_test_df,
    ) = train_test_split(
        X,
        y,
        scenario_ids,
        test_size=0.2,
        random_state=42,
    )

    print("=" * 60)
    print("Saving processed datasets")
    print("=" * 60)

    X_train.to_csv(x_train.path, index=False)

    X_test.to_csv(x_test.path, index=False)

    y_train_df.to_frame("score").to_csv(
        y_train.path,
        index=False,
    )

    y_test_df.to_frame("score").to_csv(
        y_test.path,
        index=False,
    )

    scenario_test_df.to_frame("scenario_id").to_csv(
        scenario_test.path,
        index=False,
    )

    print("Preprocessing Completed")

    print(f"Training Samples : {len(X_train)}")
    print(f"Testing Samples  : {len(X_test)}")