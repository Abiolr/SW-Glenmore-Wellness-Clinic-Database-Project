from fastapi import APIRouter

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("/", response_model=list)
def list_staff():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/staff")

@router.get("/")
async def list_staff():
    return {"staff": []}
