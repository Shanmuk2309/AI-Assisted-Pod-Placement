single_node_scenario = {
    "scenario_id": "single-node",
    "difficulty": "easy",

    "nodes": [
        {
            "name": "node1",
            "zone": "zone-a",

            "cpu_capacity": 16,
            "cpu_used": 4,

            "mem_capacity": 32,
            "mem_used": 8,

            "load": 0.2
        }
    ],

    "latency_matrix": {
        "node1": {
            "node1": 1
        }
    },

    "workload": {
        "cu": {
            "cpu_req": 2,
            "mem_req": 2
        },

        "du": {
            "cpu_req": 6,
            "mem_req": 4
        },

        "latency_budget": 5
    }
}

no_capacity_scenario = {
    "scenario_id": "no-capacity",

    "difficulty": "hard",

    "nodes": [
        {
            "name": "node1",

            "zone": "zone-a",

            "cpu_capacity": 8,
            "cpu_used": 8,

            "mem_capacity": 16,
            "mem_used": 16,

            "load": 1.0
        }
    ],

    "latency_matrix": {
        "node1": {
            "node1": 1
        }
    },

    "workload": {
        "cu": {
            "cpu_req": 4,
            "mem_req": 4
        },

        "du": {
            "cpu_req": 8,
            "mem_req": 8
        },

        "latency_budget": 5
    }
}