from fastapi import APIRouter

router = APIRouter(prefix="/procedures", tags=["procedures"])


@router.get("/")
def list_procedures():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/procedures")

@router.get("/")
async def list_procedures():
    return {"procedures": []}
