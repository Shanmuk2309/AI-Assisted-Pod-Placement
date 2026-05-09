import random
import uuid
import time



import random

def generate_nodes(num_nodes, load_factor):
    import random

    zones = ["zone-a", "zone-b", "zone-c"]   # ✅ ADD THIS

    nodes = []

    for i in range(num_nodes):
        cpu_capacity = random.randint(8, 16)
        mem_capacity = random.randint(16, 64)

        nodes.append({
            "name": f"node{i}",

            "zone": random.choice(zones),
            # inside generate_nodes()

            "load": round(random.uniform(0.1, load_factor), 2),   # ✅ ADD THIS LINE

            "cpu_capacity": cpu_capacity,
            "cpu_used": random.randint(0, int(load_factor * cpu_capacity)),

            "mem_capacity": mem_capacity,
            "mem_used": random.randint(0, int(load_factor * mem_capacity))
        })

    return nodes

def generate_latency_matrix(nodes):
    latency = {}

    for n1 in nodes:
        latency[n1["name"]] = {}

        for n2 in nodes:
            if n1["name"] == n2["name"]:
                latency[n1["name"]][n2["name"]] = 1
            elif n1["zone"] == n2["zone"]:
                latency[n1["name"]][n2["name"]] = random.randint(2, 4)
            else:
                latency[n1["name"]][n2["name"]] = random.randint(6, 10)

    return latency


# generator.py

def generate_workload(scale, latency_budget):
    import random

    return {
        "cu": {
            "cpu_req": int(random.randint(1, 3) * scale),   # ✅ lighter
            "mem_req": int(random.randint(1, 4) * scale)
        },
        "du": {
            "cpu_req": int(random.randint(4, 8) * scale),   # ✅ heavier
            "mem_req": int(random.randint(2, 6) * scale)
        },
        "latency_budget": latency_budget
    }


import uuid
import random


import uuid

def generate_scenario(difficulty="medium"):
    import uuid
    import random

    if difficulty == "easy":
        
        num_nodes = random.randint(4,6)
        load_factor = 0.3
        workload_scale = 0.5
        latency_budget = random.randint(10, 20)

    elif difficulty == "medium":
        num_nodes = random.randint(6,8)
        load_factor = 0.6
        workload_scale = 1.0
        latency_budget = random.randint(5, 15)

    elif difficulty == "hard":
        num_nodes = random.randint(8,10)
        load_factor = 0.8
        workload_scale = 1.5
        latency_budget = random.randint(2, 10)

    else:
        raise ValueError("Invalid difficulty")

    nodes = generate_nodes(num_nodes, load_factor)
    latency_matrix = generate_latency_matrix(nodes)
    workload = generate_workload(workload_scale, latency_budget)

    return {
        "scenario_id": str(uuid.uuid4()),
        "difficulty": difficulty,   # ✅ added
        "nodes": nodes,
        "latency_matrix": latency_matrix,
        "workload": workload
    }


def generate_scenarios(count):
    scenarios = []

    for i in range(count):
        if i % 3 == 0:
            diff = "easy"
        elif i % 3 == 1:
            diff = "medium"
        else:
            diff = "hard"

        scenarios.append(generate_scenario(diff))

    return scenarios