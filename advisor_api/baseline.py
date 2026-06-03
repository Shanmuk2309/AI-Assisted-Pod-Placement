from scenario_service.scorer import compute_score


def recommend_baseline(scenario):

    node_names = [
        n["name"]
        for n in scenario["nodes"]
    ]

    best_score = float("inf")
    best_placement = None

    for cu_node in node_names:

        for du_node in node_names:

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

    return {
        "method": "baseline",
        "score": best_score,
        "placement": best_placement
    }