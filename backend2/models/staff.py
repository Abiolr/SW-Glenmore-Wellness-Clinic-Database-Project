from pydantic import BaseModel

class Staff(BaseModel):
    Staff_Id: int
    First_Name: str
    Last_Name: str
    Email: str | None = None
    Active: bool = True
