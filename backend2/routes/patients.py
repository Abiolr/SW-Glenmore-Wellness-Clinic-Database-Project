from fastapi import APIRouter

router = APIRouter(prefix="/patients")

@router.get("/")
async def list_patients():
    return {"patients": []}
