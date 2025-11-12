from fastapi import APIRouter

router = APIRouter(prefix="/diagnoses")

@router.get("/")
async def list_diagnoses():
    return {"diagnoses": []}
