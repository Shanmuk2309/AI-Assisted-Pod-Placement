import ray
import pandas as pd
import os
import json

from scenario_service.storage import (
    get_unprocessed_scenarios,
    mark_scenarios_processed
)

from ray_evaluator.ray_tasks import process_scenario


def generate_dataset_parallel():

    print("\n=== DATASET GENERATION STARTED ===")

    ray.init(ignore_reinit_error=True)

    scenarios = get_unprocessed_scenarios()

    if not scenarios:
        return {
            "message": "No unprocessed scenarios found"
        }

    print(f"Scenarios fetched: {len(scenarios)}")

    # Parallel execution
    futures = [process_scenario.remote(sc) for sc in scenarios]

    print("Running parallel Ray evaluation...")

    results = ray.get(futures)

    print("Ray evaluation completed")

    # Flatten rows
    all_rows = [
        row
        for sublist in results
        for row in sublist
    ]

    print(f"Total rows generated: {len(all_rows)}")

    # Create data directory
    os.makedirs("data", exist_ok=True)

    # =========================
    # SAVE CSV
    # =========================
    df = pd.DataFrame(all_rows)

    csv_path = "data/dataset.csv"

    df.to_csv(csv_path, index=False)

    print(f"CSV dataset saved: {csv_path}")

    # =========================
    # SAVE JSONL
    # =========================
    jsonl_path = "data/dataset.jsonl"

    with open(jsonl_path, "w") as f:

        for row in all_rows:
            f.write(json.dumps(row) + "\n")

    print(f"JSONL dataset saved: {jsonl_path}")

    # =========================
    # MARK PROCESSED
    # =========================
    scenario_ids = [
        s["scenario_id"]
        for s in scenarios
    ]

    mark_scenarios_processed(scenario_ids)

    print("Scenarios marked processed")

    return {
        "rows_generated": len(all_rows),
        "scenarios_used": len(scenarios),
        "csv_file": csv_path,
        "jsonl_file": jsonl_path
    }