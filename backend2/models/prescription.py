from pydantic import BaseModel

class Prescription(BaseModel):
    Prescription_Id: int
    Patient_Id: int
    Medication: str
    Dosage: str
