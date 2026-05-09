import ray
import pandas as pd
import os
from scenario_service.storage import (
    get_unprocessed_scenarios,
    mark_scenarios_processed
)
from ray_evaluator.ray_tasks import process_scenario


def generate_dataset_parallel():
    print("\n=== DATASET GENERATION STARTED ===")
    ray.init(ignore_reinit_error=True)

    scenarios = get_unprocessed_scenarios()

    futures = [process_scenario.remote(sc) for sc in scenarios]
    print("Running parallel Ray evaluation...")

    results = ray.get(futures)
    print("Ray evaluation completed")

    all_rows = [row for sublist in results for row in sublist]

    df = pd.DataFrame(all_rows)
    df.to_csv("data/dataset.csv", index=False)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/dataset.csv", index=False)
    print("Dataset saved successfully")
    print(f"Total rows generated: {len(df)}")

    scenario_ids = [s["scenario_id"] for s in scenarios]
    mark_scenarios_processed(scenario_ids)

    return {
        "rows_generated": len(df),
        "scenarios_used": len(scenarios)
    }