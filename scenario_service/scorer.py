from scenario_service.features import extract_features


def compute_score(cu_node, du_node, scenario):
    f = extract_features(cu_node, du_node, scenario)

    if (
        f["cu_cpu_violation"] or
        f["cu_mem_violation"] or
        f["du_cpu_violation"] or
        f["du_mem_violation"]
    ):
        return 100

    latency = f["latency_ms"]
    budget = scenario["workload"]["latency_budget"]

    latency_penalty = max(0, latency - budget)

    # Resource pressure
    
    cu_cpu_util = 1 - f["cu_cpu_free_ratio"]
    du_cpu_util = 1 - f["du_cpu_free_ratio"]
    cu_mem_util = 1 - f["cu_mem_free_ratio"]
    du_mem_util = 1 - f["du_mem_free_ratio"]

    resource_pressure = (
        cu_cpu_util +
        du_cpu_util +
        cu_mem_util +
        du_mem_util
    ) / 4

    # Concentration penalty
    if cu_node == du_node:
        concentration_penalty = 0.5 * resource_pressure
    else:
        concentration_penalty = 0

    # Final score
    score = latency_penalty + resource_pressure + concentration_penalty

    return score


def evaluate_scenario(scenario):
    node_names = [n["name"] for n in scenario["nodes"]]

    results = []
    best_score = float("inf")
    best_placement = None

    for cu_node in node_names:
        for du_node in node_names:
            features = extract_features(cu_node, du_node, scenario)
            score = compute_score(cu_node, du_node, scenario)

            result = {
                "scenario_id": scenario["scenario_id"],
                "cu_node": cu_node,
                "du_node": du_node,
                **features,
                "score": score
            }

            results.append(result)

            if score < best_score:
                best_score = score
                best_placement = {
                    "scenario_id": scenario["scenario_id"],
                    "cu_node": cu_node,
                    "du_node": du_node,
                    **features
                }

    return {
        "scenario_id": scenario["scenario_id"],
        "best_score": best_score,
        "best_placement": best_placement,
        "all_results": results
    }