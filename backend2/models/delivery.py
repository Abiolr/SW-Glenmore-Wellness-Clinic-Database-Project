from pydantic import BaseModel

class Delivery(BaseModel):
    Delivery_Id: int
    Patient_Id: int
    Address: str
