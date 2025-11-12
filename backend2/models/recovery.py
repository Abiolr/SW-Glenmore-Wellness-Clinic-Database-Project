from typing import Optional
from .base import BaseModel


class Recovery(BaseModel):
    patient_id: int
    status: Optional[str] = None
    notes: Optional[str] = None
from pydantic import BaseModel

class Recovery(BaseModel):
    Recovery_Id: int
    Patient_Id: int
    Notes: str | None = None
