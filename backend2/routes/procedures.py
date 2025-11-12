from fastapi import APIRouter

router = APIRouter(prefix="/procedures")

@router.get("/")
async def list_procedures():
    return {"procedures": []}
