from fastapi import APIRouter

router = APIRouter(prefix="/staff")

@router.get("/")
async def list_staff():
    return {"staff": []}
