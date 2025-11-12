from fastapi import APIRouter

router = APIRouter(prefix="/lab")

@router.get("/")
async def list_lab():
    return {"lab": []}
