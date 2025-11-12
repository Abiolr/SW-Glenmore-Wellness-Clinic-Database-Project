from fastapi import APIRouter

router = APIRouter(prefix="/recovery", tags=["recovery"])


@router.get("/")
def list_recoveries():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/recovery")

@router.get("/")
async def list_recovery():
    return {"recovery": []}
