from fastapi import APIRouter

router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])


@router.get("/")
def list_diagnoses():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/diagnoses")

@router.get("/")
async def list_diagnoses():
    return {"diagnoses": []}
