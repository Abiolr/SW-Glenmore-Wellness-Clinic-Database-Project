from pydantic import BaseModel

class BillingCreate(BaseModel):
    patient_id: int
    amount: float
