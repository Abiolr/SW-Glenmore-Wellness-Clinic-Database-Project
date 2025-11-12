from pydantic import BaseModel

class Appointment(BaseModel):
    Appointment_Id: int
    Patient_Id: int
    Staff_Id: int
    Start: str
    End: str | None = None
