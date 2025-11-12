from pydantic import BaseModel

class AppointmentCreate(BaseModel):
    patient_id: int
    staff_id: int
    start: str
