from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=List[dict])
def list_patients():
    # placeholder
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/patients")

@router.get("/")
async def list_patients():
    return {"patients": []}
