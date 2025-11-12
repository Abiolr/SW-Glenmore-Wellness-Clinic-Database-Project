from pydantic import BaseModel
from typing import Optional


class BillingCreate(BaseModel):
    patient_id: int
    amount: float


class BillingRead(BillingCreate):
    id: Optional[int]
from pydantic import BaseModel

class BillingCreate(BaseModel):
    patient_id: int
    amount: float
