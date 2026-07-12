# AI-Assisted Pod Placement Advisor

## Overview

AI-Assisted Pod Placement Advisor is a machine learning-based Kubernetes scheduling framework that recommends optimal placements for Cloud Unit (CU) and Distributed Unit (DU) workloads.

Instead of relying solely on a manually designed scoring function, the system learns scheduling behavior from simulated Kubernetes cluster scenarios and predicts the best placement using trained machine learning models. The project also provides a baseline heuristic scheduler for comparison.

The complete workflow includes:

* Scenario generation
* Feature extraction
* Baseline scoring
* Parallel dataset generation using Ray
* Model training using Kubeflow Pipelines
* Model storage in MinIO
* ML-powered placement recommendations through FastAPI

---

# Architecture

```
                    +----------------------+
                    | Scenario Generator   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Scenario Database    |
                    | (SQLite)             |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Ray Dataset Builder  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Dataset (CSV/JSONL)  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Kubeflow Pipeline    |
                    | Random Forest / XGB  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | MinIO Model Storage  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Advisor API          |
                    | Baseline + ML        |
                    +----------------------+
```

---

# Features

* Synthetic Kubernetes cluster scenario generation
* Configurable Easy, Medium and Hard workloads
* Resource-aware placement scoring
* Parallel dataset generation using Ray
* Random Forest regression model
* XGBoost regression model
* Kubeflow Pipeline based model training
* MinIO artifact storage
* Baseline heuristic scheduler
* ML-based scheduler
* FastAPI REST APIs
* SQLite scenario persistence

---

# Project Structure

```
project/
│
├── advisor_api/
│   ├── baseline.py
│   ├── ml_predictor.py
│   ├── model_loader.py
│   ├── scenario_client.py
│   └── main.py
│
├── scenario_service/
│   ├── generator.py
│   ├── features.py
│   ├── scorer.py
│   ├── storage.py
│   ├── db.py
│   └── main.py
│
├── ray_evaluator/
│   ├── ray_tasks.py
│   └── dataset_runner.py
│
├── trainer/
│   ├── train.py
│   ├── pipeline.py
│   ├── pipeline.yaml
│   └── requirements.txt
│
├── xgboost/
│   ├── train.py
│   ├── pipeline.py
│   └── xgb_pipeline.yaml
│
└── README.md
```

---

# Workflow

## Step 1 – Generate Scenarios

Synthetic Kubernetes cluster scenarios are generated with varying:

* Number of nodes
* CPU capacity
* Memory capacity
* Current utilization
* Zones
* Network latency
* CU workload
* DU workload

Each scenario is categorized as:

* Easy
* Medium
* Hard

---

## Step 2 – Feature Extraction

For every possible CU-DU placement, the following features are extracted:

* CPU free ratio
* Memory free ratio
* Resource violations
* Network latency
* Latency budget
* Same node indicator
* Same zone indicator
* Cluster load
* CPU balance
* Memory balance
* Workload requirements

---

## Step 3 – Baseline Scoring

A handcrafted scoring function evaluates every valid placement using:

* Resource utilization
* Capacity violations
* Network latency
* Same-node penalty
* Cluster balance
* Load imbalance
* Same-zone bonus

The placement with the lowest score is selected as the optimal placement.

---

## Step 4 – Parallel Dataset Generation

Ray distributes scenario evaluation across multiple workers.

Each scenario produces every possible:

```
CU Node
×

DU Node
```

combination.

Generated datasets are exported as:

* CSV
* JSONL

---

## Step 5 – Model Training

Kubeflow Pipelines execute containerized training jobs.

Supported models:

* Random Forest Regressor
* XGBoost Regressor

Training pipeline:

1. Download dataset from MinIO
2. Train model
3. Evaluate performance
4. Save metrics
5. Upload trained model back to MinIO

---

## Step 6 – Prediction

The Advisor API:

1. Downloads the trained model from MinIO
2. Generates features for every valid placement
3. Predicts placement score
4. Returns the placement with the minimum predicted score

---

# REST APIs

## Scenario Service

Generate scenarios

```
POST /scenarios/generate?count=100
```

List scenarios

```
GET /scenarios
```

Get scenario

```
GET /scenarios/{scenario_id}
```

Evaluate scenario

```
GET /evaluate/{scenario_id}
```

Generate dataset

```
POST /dataset/generate
```

Clear scenarios

```
DELETE /scenarios/clear
```

---

## Advisor API

Baseline recommendation

```
GET /recommend/baseline/{scenario_id}
```

ML recommendation

```
GET /recommend/ml/{scenario_id}
```

---

# Machine Learning Models

## Random Forest

* Ensemble regression model
* Parallel tree construction
* Robust against noisy synthetic data

## XGBoost

* Gradient boosting decision trees
* Better generalization
* Faster inference
* Higher prediction accuracy

---

# Technologies Used

* Python
* FastAPI
* Ray
* Kubernetes
* Kubeflow Pipelines
* MinIO
* Scikit-learn
* XGBoost
* SQLAlchemy
* SQLite
* Pandas
* NumPy
* Docker

---

# Future Improvements

* Integration with a live Kubernetes cluster
* Real scheduler plugin
* Reinforcement Learning based placement
* Multi-objective optimization
* GPU-aware scheduling
* Energy-aware scheduling
* Online model retraining
* Prometheus metrics integration
* Grafana dashboard

---

# Authors

**Kaushik Reddy**
**Shanmuk**
**Thejeswar**
**B Umesh**

Department of Computer Science and Engineering

M. S. Ramaiah Institute of Technology

---

# License

This project is developed for academic research and educational purposes.
