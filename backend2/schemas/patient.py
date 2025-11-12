from pydantic import BaseModel

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    dob: str | None = None
