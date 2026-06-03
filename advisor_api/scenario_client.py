import requests

SCENARIO_SERVICE_URL = "http://localhost:8000"


def get_scenario(scenario_id: str):

    response = requests.get(
        f"{SCENARIO_SERVICE_URL}/scenarios/{scenario_id}"
    )

    response.raise_for_status()

    return response.json()