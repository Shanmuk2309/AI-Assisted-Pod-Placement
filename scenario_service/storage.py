from scenario_service.db import SessionLocal, Scenario


def save_scenarios(scenarios):
    db = SessionLocal()
    for sc in scenarios:
        db.add(Scenario(
            scenario_id=sc["scenario_id"],
            data=sc
        ))

    db.commit()
    db.close()


def get_all_scenarios():
    db = SessionLocal()
    data = db.query(Scenario).all()
    db.close()

    return [d.data for d in data]

def get_scenario_by_id(scenario_id: str):
    db = SessionLocal()
    result = db.query(Scenario).filter(Scenario.scenario_id == scenario_id).first()
    db.close()

    return result.data if result else None


def get_unprocessed_scenarios():
    db = SessionLocal()

    scenarios = (
        db.query(Scenario)
        .filter(Scenario.processed == False)
        .all()
    )

    db.close()

    return [s.data for s in scenarios]

def mark_scenarios_processed(scenario_ids):
    db = SessionLocal()

    scenarios = (
        db.query(Scenario)
        .filter(Scenario.scenario_id.in_(scenario_ids))
        .all()
    )

    for s in scenarios:
        s.processed = True

    db.commit()
    db.close()