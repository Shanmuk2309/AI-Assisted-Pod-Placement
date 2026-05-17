# features.py

def extract_features(cu_node, du_node, scenario):

    nodes = {
        n["name"]: n
        for n in scenario["nodes"]
    }

    latency_matrix = scenario["latency_matrix"]
    workload = scenario["workload"]

    cu = workload["cu"]
    du = workload["du"]

    n1 = nodes[cu_node]
    n2 = nodes[du_node]

    # =========================
    # CPU AFTER PLACEMENT
    # =========================

    cu_cpu_used = n1["cpu_used"] + cu["cpu_req"]
    du_cpu_used = n2["cpu_used"] + du["cpu_req"]

    cu_cpu_free_ratio = 1 - (
        cu_cpu_used / n1["cpu_capacity"]
    )

    du_cpu_free_ratio = 1 - (
        du_cpu_used / n2["cpu_capacity"]
    )

    # =========================
    # MEMORY AFTER PLACEMENT
    # =========================

    cu_mem_used = n1["mem_used"] + cu["mem_req"]
    du_mem_used = n2["mem_used"] + du["mem_req"]

    cu_mem_free_ratio = 1 - (
        cu_mem_used / n1["mem_capacity"]
    )

    du_mem_free_ratio = 1 - (
        du_mem_used / n2["mem_capacity"]
    )

    # =========================
    # VIOLATIONS
    # =========================

    cu_cpu_violation = (
        1 if cu_cpu_used > n1["cpu_capacity"]
        else 0
    )

    du_cpu_violation = (
        1 if du_cpu_used > n2["cpu_capacity"]
        else 0
    )

    cu_mem_violation = (
        1 if cu_mem_used > n1["mem_capacity"]
        else 0
    )

    du_mem_violation = (
        1 if du_mem_used > n2["mem_capacity"]
        else 0
    )

    # =========================
    # LATENCY
    # =========================

    latency_ms = latency_matrix[cu_node][du_node]

    same_node = 1 if cu_node == du_node else 0

    same_zone = (
        1 if n1["zone"] == n2["zone"]
        else 0
    )

        # =========================
    # CLUSTER BALANCE
    # =========================

    cpu_utils = []
    mem_utils = []

    for node in scenario["nodes"]:

        cpu_used = node["cpu_used"]
        mem_used = node["mem_used"]

        # Simulate placement impact
        if node["name"] == cu_node:

            cpu_used += cu["cpu_req"]
            mem_used += cu["mem_req"]

        if node["name"] == du_node:

            cpu_used += du["cpu_req"]
            mem_used += du["mem_req"]

        cpu_util = (
            cpu_used / node["cpu_capacity"]
        )

        mem_util = (
            mem_used / node["mem_capacity"]
        )

        cpu_utils.append(cpu_util)
        mem_utils.append(mem_util)

    # Average cluster utilization
    avg_cpu = sum(cpu_utils) / len(cpu_utils)
    avg_mem = sum(mem_utils) / len(mem_utils)

    # Variance = imbalance
    cpu_balance = sum(
        (u - avg_cpu) ** 2
        for u in cpu_utils
    ) / len(cpu_utils)

    mem_balance = sum(
        (u - avg_mem) ** 2
        for u in mem_utils
    ) / len(mem_utils)

    # =========================
    # RETURN FEATURES
    # =========================

    return {

        # Core ratios
        "cu_cpu_free_ratio": cu_cpu_free_ratio,
        "du_cpu_free_ratio": du_cpu_free_ratio,

        "cu_mem_free_ratio": cu_mem_free_ratio,
        "du_mem_free_ratio": du_mem_free_ratio,

        # Latency
        "latency_ms": latency_ms,
        "latency_budget": workload["latency_budget"],

        # Placement relationship
        "same_node": same_node,
        "same_zone": same_zone,

        # Node load
        "cu_load": n1.get("load", 0),
        "du_load": n2.get("load", 0),

        # Violations
        "cu_cpu_violation": cu_cpu_violation,
        "cu_mem_violation": cu_mem_violation,
        "du_cpu_violation": du_cpu_violation,
        "du_mem_violation": du_mem_violation,

        # Capacities
        "cu_cpu_capacity": n1["cpu_capacity"],
        "du_cpu_capacity": n2["cpu_capacity"],

        "cu_mem_capacity": n1["mem_capacity"],
        "du_mem_capacity": n2["mem_capacity"],

        # Post-placement utilization
        "cu_cpu_used_after": cu_cpu_used,
        "du_cpu_used_after": du_cpu_used,

        "cu_mem_used_after": cu_mem_used,
        "du_mem_used_after": du_mem_used,

        "cpu_balance": cpu_balance,
        "mem_balance": mem_balance,

        # Workload requirements
        "cu_cpu_req": cu["cpu_req"],
        "du_cpu_req": du["cpu_req"],

        "cu_mem_req": cu["mem_req"],
        "du_mem_req": du["mem_req"]
    }