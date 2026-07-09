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
dataset_status = {
    "status": "idle",
    "message": "Dataset has not been generated yet.",
    "rows_generated": None,
    "scenarios_used": None,
    "csv_file": None,
    "jsonl_file": None,
    "error": None,
}

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

def run_dataset_generation():
    global dataset_status

    dataset_status = {
        "status": "running",
        "message": "Generating dataset...",
        "rows_generated": None,
        "scenarios_used": None,
        "csv_file": None,
        "jsonl_file": None,
        "error": None,
    }

    try:
        result = generate_dataset_parallel()

        dataset_status = {
            "status": "completed",
            "message": "Dataset generated successfully.",
            "rows_generated": result.get("rows_generated"),
            "scenarios_used": result.get("scenarios_used"),
            "csv_file": result.get("csv_file"),
            "jsonl_file": result.get("jsonl_file"),
            "error": None,
        }

    except Exception as e:

        dataset_status = {
            "status": "failed",
            "message": "Dataset generation failed.",
            "rows_generated": None,
            "scenarios_used": None,
            "csv_file": None,
            "jsonl_file": None,
            "error": str(e),
        }

@app.post("/dataset/generate")
def generate_dataset(background_tasks: BackgroundTasks):

    background_tasks.add_task(run_dataset_generation)

    return {
        "message": "Dataset generation started"
    }

@app.get("/dataset/status")
def get_dataset_status():
    return dataset_status

from scenario_service.db import SessionLocal, Scenario

@app.delete("/scenarios/clear")
def clear_scenarios():
    db = SessionLocal()
    db.query(Scenario).delete()
    db.commit()
    db.close()
    return {"message": "All scenarios deleted"}