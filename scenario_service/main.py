from ray_evaluator.dataset_runner import generate_dataset_parallel
from fastapi import FastAPI
from fastapi import BackgroundTasks
from scenario_service.scorer import evaluate_scenario
from scenario_service.generator import generate_scenarios
import scenario_service.db
from scenario_service.storage import (
    save_scenarios,
    get_all_scenarios,
    get_scenario_by_id
)

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
    return {"message": "Scenario Service Running "}


# Generate scenarios
@app.post("/scenarios/generate")
def generate(count: int = 10):
    scenarios = generate_scenarios(count)
    save_scenarios(scenarios)

    return {
        "message": f"{count} scenarios generated",
        "count": count
    }


# Get all scenarios
@app.get("/scenarios")
def get_all():
    return get_all_scenarios()


# Get specific scenario
@app.get("/scenarios/{scenario_id}")
def get_one(scenario_id: str):
    scenario = get_scenario_by_id(scenario_id)

    if not scenario:
        return {"error": "Scenario not found"}

    return scenario

@app.get("/evaluate/{scenario_id}")
def evaluate(scenario_id: str):
    scenario = get_scenario_by_id(scenario_id)

    if not scenario:
        return {"error": "Scenario not found"}
    
    return evaluate_scenario(scenario)


@app.post("/dataset/generate")
def generate_dataset(background_tasks: BackgroundTasks):

    background_tasks.add_task(generate_dataset_parallel)

    return {
        "message": "Dataset generation started"
    }

from scenario_service.db import SessionLocal, Scenario

@app.delete("/scenarios/clear")
def clear_scenarios():
    db = SessionLocal()
    db.query(Scenario).delete()
    db.commit()
    db.close()
    return {"message": "All scenarios deleted"}