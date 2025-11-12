from pydantic import BaseModel

class Lab(BaseModel):
    Lab_Id: int
    Patient_Id: int
    Test_Name: str
    Result: str | None = None
