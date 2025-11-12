from pydantic import BaseModel

class Patient(BaseModel):
    Patient_Id: int
    First_Name: str
    Last_Name: str
    Date_Of_Birth: str | None = None
