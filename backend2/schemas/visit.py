from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VisitCreate(BaseModel):
    appointment_id: int
    notes: Optional[str] = None


class VisitRead(VisitCreate):
    id: Optional[int]
    seen_at: Optional[datetime]
from pydantic import BaseModel

class VisitCreate(BaseModel):
    patient_id: int
    notes: str | None = None
