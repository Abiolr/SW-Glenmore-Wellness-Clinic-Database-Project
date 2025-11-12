from fastapi import APIRouter

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


@router.get("/")
def list_prescriptions():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/prescriptions")

@router.get("/")
async def list_prescriptions():
    return {"prescriptions": []}
