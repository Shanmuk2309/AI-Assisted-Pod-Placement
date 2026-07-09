from fastapi import FastAPI

from advisor_api.baseline import recommend_baseline
from advisor_api.ml_predictor import recommend_ml
from advisor_api.scenario_client import get_scenario

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():

    return {
        "message": "Advisor API Running"
    }


@app.get("/recommend/baseline/{scenario_id}")
def baseline_route(scenario_id: str):

    scenario = get_scenario(
        scenario_id
    )

    return recommend_baseline(
        scenario
    )


@app.get("/recommend/ml/{scenario_id}")
def ml_route(scenario_id: str):

    scenario = get_scenario(
        scenario_id
    )

    return recommend_ml(
        scenario
    )