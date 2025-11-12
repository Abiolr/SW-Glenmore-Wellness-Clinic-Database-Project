from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AppointmentCreate(BaseModel):
    patient_id: int
    start_time: Optional[datetime] = None


class AppointmentRead(AppointmentCreate):
    id: Optional[int]
from pydantic import BaseModel

class AppointmentCreate(BaseModel):
    patient_id: int
    staff_id: int
    start: str
