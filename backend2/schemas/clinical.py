from pydantic import BaseModel
from typing import Optional


class ClinicalNote(BaseModel):
    visit_id: int
    note: Optional[str]
from pydantic import BaseModel

class ClinicalNote(BaseModel):
    note: str
