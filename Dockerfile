FROM rayproject/ray:2.9.3-py310

WORKDIR /app

COPY requirements-ray.txt .

RUN pip install --no-cache-dir -r requirements-ray.txt

COPY scenario_service ./scenario_service
COPY ray_evaluator ./ray_evaluator

ENV PYTHONPATH=/app