import pandas as pd

from advisor_api.model_loader import load_model
from scenario_service.features import extract_features

model = load_model()

difficulty_mapping = {
    "easy": 0,
    "medium": 1,
    "hard": 2
}


def recommend_ml(scenario):

    node_names = [
        n["name"]
        for n in scenario["nodes"]
    ]

    best_score = float("inf")
    best_placement = None

    for cu_node in node_names:

        for du_node in node_names:

            features = extract_features(
                cu_node,
                du_node,
                scenario
            )

            row = {

                "difficulty": difficulty_mapping[
                    scenario["difficulty"]
                ],

                "cu_cpu_free_ratio":
                    features["cu_cpu_free_ratio"],

                "du_cpu_free_ratio":
                    features["du_cpu_free_ratio"],

                "cu_mem_free_ratio":
                    features["cu_mem_free_ratio"],

                "du_mem_free_ratio":
                    features["du_mem_free_ratio"],

                "latency_ms":
                    features["latency_ms"],

                "latency_budget":
                    features["latency_budget"],

                "same_node":
                    features["same_node"],

                "same_zone":
                    features["same_zone"],

                "cu_load":
                    features["cu_load"],

                "du_load":
                    features["du_load"],

                "cu_cpu_violation":
                    features["cu_cpu_violation"],

                "cu_mem_violation":
                    features["cu_mem_violation"],

                "du_cpu_violation":
                    features["du_cpu_violation"],

                "du_mem_violation":
                    features["du_mem_violation"],

                "cpu_balance":
                    features["cpu_balance"],

                "mem_balance":
                    features["mem_balance"],

                "cu_cpu_req":
                    features["cu_cpu_req"],

                "du_cpu_req":
                    features["du_cpu_req"],

                "cu_mem_req":
                    features["cu_mem_req"],

                "du_mem_req":
                    features["du_mem_req"]
            }

            prediction = model.predict(
                pd.DataFrame([row])
            )[0]

            if prediction < best_score:

                best_score = prediction

                best_placement = {
                    "cu_node": cu_node,
                    "du_node": du_node
                }

    return {
        "method": "ml",
        "predicted_score": float(best_score),
        "placement": best_placement
    }