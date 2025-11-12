from pydantic import BaseModel

class VisitCreate(BaseModel):
    patient_id: int
    notes: str | None = None
