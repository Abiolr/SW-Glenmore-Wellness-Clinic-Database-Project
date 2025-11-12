from fastapi import APIRouter

router = APIRouter(prefix="/lab", tags=["lab"])


@router.get("/")
def list_labs():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/lab")

@router.get("/")
async def list_lab():
    return {"lab": []}
