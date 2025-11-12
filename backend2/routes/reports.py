from fastapi import APIRouter

router = APIRouter(prefix="/reports")

@router.get("/")
async def list_reports():
    return {"reports": []}
