from pydantic import BaseModel
from typing import Optional


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    dob: Optional[str] = None


class PatientRead(PatientCreate):
    id: Optional[int]
from pydantic import BaseModel

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    dob: str | None = None
