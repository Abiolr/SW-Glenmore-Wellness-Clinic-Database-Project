from typing import Optional
from pydantic import BaseModel


class IDModel(BaseModel):
    id: Optional[int]
from pydantic import BaseModel

class IDSchema(BaseModel):
    id: int
