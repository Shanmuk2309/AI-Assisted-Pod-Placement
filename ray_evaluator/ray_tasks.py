import ray

from scenario_service.features import extract_features
from scenario_service.scorer import compute_score


@ray.remote
def process_scenario(scenario):

    rows = []

    node_names = [
        n["name"]
        for n in scenario["nodes"]
    ]

    for cu_node in node_names:

        for du_node in node_names:

            features = extract_features(
                cu_node,
                du_node,
                scenario
            )

            score = compute_score(
                cu_node,
                du_node,
                scenario
            )

            row = {
                "scenario_id": scenario["scenario_id"],
                "difficulty": scenario["difficulty"],
                "cu_node": cu_node,
                "du_node": du_node,
                **features,
                "score": score
            }

            rows.append(row)

    return rows