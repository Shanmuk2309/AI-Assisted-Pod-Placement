# features.py

def extract_features(cu_node, du_node, scenario):
    nodes = {n["name"]: n for n in scenario["nodes"]}
    latency_matrix = scenario["latency_matrix"]
    workload = scenario["workload"]

    cu = workload["cu"]
    du = workload["du"]

    n1 = nodes[cu_node]
    n2 = nodes[du_node]

    # CPU after placement
    cu_cpu_used = n1["cpu_used"] + cu["cpu_req"]
    du_cpu_used = n2["cpu_used"] + du["cpu_req"]

    cu_cpu_free_ratio = 1 - (cu_cpu_used / n1["cpu_capacity"])
    du_cpu_free_ratio = 1 - (du_cpu_used / n2["cpu_capacity"])

    # MEMORY after placement
    cu_mem_used = n1["mem_used"] + cu["mem_req"]
    du_mem_used = n2["mem_used"] + du["mem_req"]

    cu_mem_free_ratio = 1 - (cu_mem_used / n1["mem_capacity"])
    du_mem_free_ratio = 1 - (du_mem_used / n2["mem_capacity"])

    # Violations
    cu_cpu_violation = 1 if cu_cpu_used > n1["cpu_capacity"] else 0
    du_cpu_violation = 1 if du_cpu_used > n2["cpu_capacity"] else 0
    cu_mem_violation = 1 if cu_mem_used > n1["mem_capacity"] else 0
    du_mem_violation = 1 if du_mem_used > n2["mem_capacity"] else 0

    latency_ms = latency_matrix[cu_node][du_node]

    same_node = 1 if cu_node == du_node else 0
    same_zone = 1 if n1["zone"] == n2["zone"] else 0

    return {
        "cu_cpu_free_ratio": cu_cpu_free_ratio,
        "du_cpu_free_ratio": du_cpu_free_ratio,
        "cu_mem_free_ratio": cu_mem_free_ratio,
        "du_mem_free_ratio": du_mem_free_ratio,
        "latency_ms": latency_ms,
        "same_node": same_node,
        "same_zone": same_zone,
        "cu_load": n1.get("load", 0),
        "du_load": n2.get("load", 0),
        "cu_cpu_violation": cu_cpu_violation,
        "cu_mem_violation": cu_mem_violation,
        "du_cpu_violation": du_cpu_violation,
        "du_mem_violation": du_mem_violation
    }