from scenario_service.features import extract_features
from scenario_service.scorer import compute_score

def get_baseline_rankings(scenario):

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

            score = compute_score(
                cu_node,
                du_node,
                scenario
            )

            rankings.append({
                "cu_node": cu_node,
                "du_node": du_node,
                "score": score
            })

    return sorted(
        rankings,
        key=lambda x: x["score"]
    )


def recommend_baseline(scenario):

    node_names = [n["name"] for n in scenario["nodes"]]

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

            if violations == 0:
                valid_found = True

            score = compute_score(
                cu_node,
                du_node,
                scenario
            )

            if score < best_score:
                best_score = score
                best_placement = {
                    "cu_node": cu_node,
                    "du_node": du_node
                }

    if not valid_found:

        return {
            "status": "NO_VALID_PLACEMENT",
            "reason": "Insufficient cluster resources"
        }

    return {
        "status": "SUCCESS",
        "method": "baseline",
        "score": best_score,
        "placement": best_placement
    }