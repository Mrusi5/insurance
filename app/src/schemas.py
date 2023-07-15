from pydantic import BaseModel
from datetime import date

class CargoTypeSchema(BaseModel):
    cargo_type: str
    rate: float


class InsuranceRequestSchema(BaseModel):
    declared_value: float
    cargo_type: str
    date: date