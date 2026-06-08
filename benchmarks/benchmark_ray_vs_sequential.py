import time
import ray
import pandas as pd
import matplotlib.pyplot as plt

from scenario_service.generator import generate_scenarios
from scenario_service.scorer import compute_score


# ----------------------------
# Sequential Processing
# ----------------------------

def process_scenario(scenario):

    nodes = [
        n["name"]
        for n in scenario["nodes"]
    ]

    best_score = float("inf")

    for cu_node in nodes:

        for du_node in nodes:

            score = compute_score(
                cu_node,
                du_node,
                scenario
            )

            if score < best_score:
                best_score = score

    return best_score


# ----------------------------
# Ray Processing
# ----------------------------

@ray.remote
def process_scenario_ray(scenario):

    nodes = [
        n["name"]
        for n in scenario["nodes"]
    ]

    best_score = float("inf")

    for cu_node in nodes:

        for du_node in nodes:

            score = compute_score(
                cu_node,
                du_node,
                scenario
            )

            if score < best_score:
                best_score = score

    return best_score


# ----------------------------
# Benchmark
# ----------------------------

def benchmark_sequential(num_scenarios):

    scenarios = generate_scenarios(
        num_scenarios
    )

    start = time.time()

    for scenario in scenarios:

        process_scenario(
            scenario
        )

    end = time.time()

    return end - start


def benchmark_ray(num_scenarios):

    scenarios = generate_scenarios(
        num_scenarios
    )

    start = time.time()

    futures = [

        process_scenario_ray.remote(
            scenario
        )

        for scenario in scenarios
    ]

    ray.get(futures)

    end = time.time()

    return end - start


# ----------------------------
# Main
# ----------------------------

def main():

    ray.init(ignore_reinit_error=True)

    sizes = [
        1000,
        5000,
        10000,
        25000,
        50000
    ]

    results = []

    print("\nBenchmarking...\n")

    for size in sizes:

        print(
            f"Running "
            f"{size} scenarios..."
        )

        seq_time = benchmark_sequential(
            size
        )

        ray_time = benchmark_ray(
            size
        )

        speedup = (
            seq_time / ray_time
        )

        print(
            f"Sequential : "
            f"{seq_time:.2f}s"
        )

        print(
            f"Ray        : "
            f"{ray_time:.2f}s"
        )

        print(
            f"Speedup    : "
            f"{speedup:.2f}x\n"
        )

        results.append({

            "scenarios":
                size,

            "sequential_time":
                seq_time,

            "ray_time":
                ray_time,

            "speedup":
                speedup
        })

    ray.shutdown()

    df = pd.DataFrame(
        results
    )

    df.to_csv(
        "ray_vs_sequential.csv",
        index=False
    )

    print(
        "\nSaved "
        "ray_vs_sequential.csv"
    )

    # ------------------------
    # Graph 1
    # ------------------------

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        df["scenarios"],
        df["sequential_time"],
        marker="o",
        label="Sequential"
    )

    plt.plot(
        df["scenarios"],
        df["ray_time"],
        marker="o",
        label="Ray"
    )

    plt.xlabel(
        "Number of Scenarios"
    )

    plt.ylabel(
        "Execution Time (seconds)"
    )

    plt.title(
        "Sequential vs Ray Processing"
    )

    plt.legend()

    plt.grid(True)

    plt.savefig(
        "ray_vs_sequential.png"
    )

    # ------------------------
    # Graph 2
    # ------------------------

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        df["scenarios"],
        df["speedup"],
        marker="o"
    )

    plt.xlabel(
        "Number of Scenarios"
    )

    plt.ylabel(
        "Speedup (x)"
    )

    plt.title(
        "Ray Speedup Over Sequential"
    )

    plt.grid(True)

    plt.savefig(
        "ray_speedup.png"
    )

    print(
        "Generated:\n"
        "- ray_vs_sequential.png\n"
        "- ray_speedup.png"
    )


if __name__ == "__main__":
    main()