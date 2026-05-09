from sqlalchemy import create_engine, Column, String, JSON, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///scenarios.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Scenario(Base):
    __tablename__ = "scenarios"

    scenario_id = Column(String, primary_key=True)
    data = Column(JSON)
    processed = Column(Boolean, default=False)

Base.metadata.create_all(engine)