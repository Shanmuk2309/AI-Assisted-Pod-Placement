import pandas as pd

from advisor_api.model_loader import load_model
from scenario_service.features import extract_features

model = load_model()

difficulty_mapping = {
    "easy": 0,
    "medium": 1,
    "hard": 2
}
def get_ml_rankings(scenario):

    node_names = [
        n["name"]
        for n in scenario["nodes"]
    ]

    rankings = []

    for cu_node in node_names:
        for du_node in node_names:

            features = extract_features(
                cu_node,
                du_node,
                scenario
            )

            violations = (
                features["cu_cpu_violation"]
                + features["cu_mem_violation"]
                + features["du_cpu_violation"]
                + features["du_mem_violation"]
            )

            if violations > 0:
                continue

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

            rankings.append({
                "cu_node": cu_node,
                "du_node": du_node,
                "predicted_score": float(prediction)
            })

    return sorted(
        rankings,
        key=lambda x: x["predicted_score"]
    )




def recommend_ml(scenario):

    node_names = [
        n["name"]
        for n in scenario["nodes"]
    ]

    best_score = float("inf")
    best_placement = None

    valid_found = False

    for cu_node in node_names:

        for du_node in node_names:

            features = extract_features(
                cu_node,
                du_node,
                scenario
            )

            violations = (
                features["cu_cpu_violation"]
                + features["cu_mem_violation"]
                + features["du_cpu_violation"]
                + features["du_mem_violation"]
            )

            # Skip invalid placements
            if violations > 0:
                continue

            valid_found = True

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

    # No feasible placement exists
    if not valid_found:

        return {
            "status": "NO_VALID_PLACEMENT",
            "reason": "Insufficient cluster resources"
        }

    return {
        "status": "SUCCESS",
        "method": "ml",
        "predicted_score": float(best_score),
        "placement": best_placement
    }