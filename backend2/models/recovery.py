from pydantic import BaseModel

class Recovery(BaseModel):
    Recovery_Id: int
    Patient_Id: int
    Notes: str | None = None
