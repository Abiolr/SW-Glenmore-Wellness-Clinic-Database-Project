from pydantic import BaseModel

class ClinicalNote(BaseModel):
    note: str
