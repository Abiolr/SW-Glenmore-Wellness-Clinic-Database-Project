from fastapi import APIRouter

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("/")
def list_deliveries():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/deliveries")

@router.get("/")
async def list_deliveries():
    return {"deliveries": []}
