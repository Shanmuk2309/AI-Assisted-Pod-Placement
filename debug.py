import pandas as pd

from scenario_service.storage import get_all_scenarios

from advisor_api.baseline import (
    recommend_baseline,
    get_baseline_rankings
)

from advisor_api.ml_predictor import (
    recommend_ml,
    get_ml_rankings,
    model
)


def placements_equal(baseline, ml):

    if (
        baseline.get("status") == "NO_VALID_PLACEMENT"
        and ml.get("status") == "NO_VALID_PLACEMENT"
    ):
        return True

    if (
        baseline.get("status") == "NO_VALID_PLACEMENT"
        or ml.get("status") == "NO_VALID_PLACEMENT"
    ):
        return False

    return (
        baseline["placement"]
        ==
        ml["placement"]
    )


def main():

    scenarios = get_all_scenarios()

    print("\n===================================")
    print("MODEL FEATURE CHECK")
    print("===================================\n")

    print(model.feature_names_in_)

    mismatches = []

    total = 0
    matches = 0

    easy = medium = hard = 0
    easy_ok = medium_ok = hard_ok = 0

    for scenario in scenarios:

        total += 1

        baseline = recommend_baseline(
            scenario
        )

        ml = recommend_ml(
            scenario
        )

        equal = placements_equal(
            baseline,
            ml
        )

        diff = scenario["difficulty"]

        if diff == "easy":
            easy += 1
        elif diff == "medium":
            medium += 1
        else:
            hard += 1

        if equal:

            matches += 1

            if diff == "easy":
                easy_ok += 1
            elif diff == "medium":
                medium_ok += 1
            else:
                hard_ok += 1

            continue

        baseline_rank = get_baseline_rankings(
            scenario
        )[:5]

        ml_rank = get_ml_rankings(
            scenario
        )[:5]

        best_gap = None

        if len(baseline_rank) >= 2:

            best_gap = (
                baseline_rank[1]["score"]
                -
                baseline_rank[0]["score"]
            )
        

        mismatches.append({

            "scenario_id":
                scenario["scenario_id"],

            "difficulty":
                diff,

            "baseline_cu":
                baseline["placement"]["cu_node"],

            "baseline_du":
                baseline["placement"]["du_node"],

            "ml_cu":
                ml["placement"]["cu_node"],

            "ml_du":
                ml["placement"]["du_node"],

            "baseline_score":
                baseline.get("score"),

            "ml_score":
                ml.get("predicted_score"),

            "best_gap":
                best_gap,

            "baseline_top5":
                str(baseline_rank),

            "ml_top5":
                str(ml_rank)
        })

    mismatch_df = pd.DataFrame(
        mismatches
    )

    mismatch_df.to_csv(
        "mismatch_analysis.csv",
        index=False
    )

    print("\n===================================")
    print("SUMMARY")
    print("===================================\n")

    print(f"Total Scenarios : {total}")
    print(f"Matches         : {matches}")
    print(f"Mismatches      : {total-matches}")

    print(
        f"Accuracy        : "
        f"{matches/total*100:.2f}%"
    )

    print("\nDifficulty Accuracy")

    print(
        f"EASY   : "
        f"{easy_ok}/{easy} "
        f"({easy_ok/easy*100:.2f}%)"
    )

    print(
        f"MEDIUM : "
        f"{medium_ok}/{medium} "
        f"({medium_ok/medium*100:.2f}%)"
    )

    print(
        f"HARD   : "
        f"{hard_ok}/{hard} "
        f"({hard_ok/hard*100:.2f}%)"
    )

    print(
        "\nSaved mismatch_analysis.csv"
    )

    small_gap = 0
    medium_gap = 0
    large_gap = 0

    for _, row in mismatch_df.iterrows():

        gap = row["best_gap"]

        if gap < 0.5:
            small_gap += 1

        elif gap < 1.5:
            medium_gap += 1

        else:
            large_gap += 1

    print("\nMismatch Gap Analysis")
    print(f"<0.5   : {small_gap}")
    print(f"0.5-1.5 : {medium_gap}")
    print(f">1.5   : {large_gap}")


if __name__ == "__main__":
    main()