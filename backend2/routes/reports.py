from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/")
def get_reports():
    return {"reports": []}
from fastapi import APIRouter

router = APIRouter(prefix="/reports")

@router.get("/")
async def list_reports():
    return {"reports": []}
