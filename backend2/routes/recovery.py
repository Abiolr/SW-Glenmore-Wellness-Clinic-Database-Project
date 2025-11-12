from fastapi import APIRouter

router = APIRouter(prefix="/recovery")

@router.get("/")
async def list_recovery():
    return {"recovery": []}
