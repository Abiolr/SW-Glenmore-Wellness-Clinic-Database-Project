from pydantic import BaseModel
from typing import Optional, List


class ReportRequest(BaseModel):
    name: str
    filters: Optional[dict] = None


class ReportResult(BaseModel):
    rows: List[dict]
from pydantic import BaseModel

class ReportRequest(BaseModel):
    start_date: str
    end_date: str
