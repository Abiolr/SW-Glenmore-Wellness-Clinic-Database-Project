from pydantic import BaseModel

class Billing(BaseModel):
    Billing_Id: int
    Patient_Id: int
    Amount: float
