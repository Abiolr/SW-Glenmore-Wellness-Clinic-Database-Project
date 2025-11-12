from pydantic import BaseModel

class Visit(BaseModel):
    Visit_Id: int
    Patient_Id: int
    Notes: str | None = None
