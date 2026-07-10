import os
import json
import ray
import pandas as pd

from minio import Minio

from scenario_service.storage import (
    get_unprocessed_scenarios,
    mark_scenarios_processed
)

from ray_evaluator.ray_tasks import process_scenario


# =====================================================
# RAY CONFIGURATION
# =====================================================

RAY_ADDRESS = os.getenv(
    "RAY_ADDRESS",
    "ray://localhost:10001"
)


# =====================================================
# MINIO CONFIGURATION
# =====================================================

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


# =====================================================
# DATASET GENERATION
# =====================================================

def generate_dataset_parallel():

    print("\n====================================")
    print("Connecting to Ray Cluster...")
    print("====================================")

    ray.init(
        address=RAY_ADDRESS,
        ignore_reinit_error=True
    )

    print("Connected Successfully!")

    print("\nCluster Resources:")
    print(ray.cluster_resources())

    scenarios = get_unprocessed_scenarios()

    if not scenarios:
        print("No unprocessed scenarios found.")
        ray.shutdown()

        return {
            "message": "No unprocessed scenarios found."
        }

    print(f"\nLoaded {len(scenarios)} scenarios.")

    batch_size = 300

    all_rows = []

    for start in range(0, len(scenarios), batch_size):

        end = min(start + batch_size, len(scenarios))

        print(f"\nProcessing scenarios {start} - {end}")

        batch = scenarios[start:end]

        futures = [
            process_scenario.remote(scenario)
            for scenario in batch
        ]

        results = ray.get(futures)

        for rows in results:
            all_rows.extend(rows)

        print(f"Completed {end}/{len(scenarios)} scenarios.")

    print("\nCreating DataFrame...")

    df = pd.DataFrame(all_rows)

    os.makedirs("data", exist_ok=True)

    csv_path = "data/dataset.csv"

    jsonl_path = "data/dataset.jsonl"

    print("Saving CSV...")

    df.to_csv(
        csv_path,
        index=False
    )

    print("Saving JSONL...")

    with open(jsonl_path, "w") as f:

        for row in all_rows:

            f.write(json.dumps(row) + "\n")

    print("\nUploading dataset to MinIO...")

    client.fput_object(
        "datasets",
        "dataset.csv",
        csv_path
    )

    client.fput_object(
        "datasets",
        "dataset.jsonl",
        jsonl_path
    )

    print("Upload completed.")

    mark_scenarios_processed(
        [
            scenario["scenario_id"]
            for scenario in scenarios
        ]
    )

    print("Scenarios marked as processed.")

    ray.shutdown()

    print("\n====================================")
    print("Dataset Generation Completed")
    print("====================================")

    return {
    "status": "SUCCESS",
    "rows_generated": len(all_rows),
    "scenarios_used": len(scenarios),
    "csv_file": csv_path,
    "jsonl_file": jsonl_path,
}