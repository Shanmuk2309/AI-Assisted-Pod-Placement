from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

from advisor_api.baseline import recommend_baseline
from advisor_api.ml_predictor import recommend_ml
from advisor_api.scenario_client import get_scenario

app = FastAPI()


class ScenarioRequest(BaseModel):
    scenario_id: str
    difficulty: str
    nodes: List[Dict[str, Any]]
    latency_matrix: Dict[str, Dict[str, Any]]
    workload: Dict[str, Any]

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

    scenario = get_scenario(scenario_id)
    return recommend_baseline(scenario)


@app.post("/recommend/baseline")
def baseline_custom(scenario: ScenarioRequest):
    return recommend_baseline(scenario.model_dump())


@app.get("/recommend/ml/{scenario_id}")
def ml_route(scenario_id: str):
    scenario = get_scenario(scenario_id)
    return recommend_ml(scenario)


@app.post("/recommend/ml")
def ml_custom(scenario: ScenarioRequest):
    return recommend_ml(scenario.model_dump())