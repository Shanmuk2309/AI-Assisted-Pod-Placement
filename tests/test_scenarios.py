from advisor_api.baseline import recommend_baseline
from advisor_api.ml_predictor import recommend_ml

from tests.edge_cases import (
    single_node_scenario,
    no_capacity_scenario
)

print("Single Node Test")
print(
    recommend_baseline(
        single_node_scenario
    )
)

print(
    recommend_ml(
        single_node_scenario
    )
)

print("\nNo Capacity Test")
print(
    recommend_baseline(
        no_capacity_scenario
    )
)

print(
    recommend_ml(
        no_capacity_scenario
    )
)