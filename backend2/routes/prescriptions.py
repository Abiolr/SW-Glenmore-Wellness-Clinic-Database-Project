from fastapi import APIRouter

router = APIRouter(prefix="/prescriptions")

@router.get("/")
async def list_prescriptions():
    return {"prescriptions": []}
