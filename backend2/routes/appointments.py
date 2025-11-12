from fastapi import APIRouter

router = APIRouter(prefix="/appointments")

@router.get("/")
async def list_appointments():
    return {"appointments": []}
