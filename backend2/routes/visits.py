from fastapi import APIRouter

router = APIRouter(prefix="/visits")

@router.get("/")
async def list_visits():
    return {"visits": []}
