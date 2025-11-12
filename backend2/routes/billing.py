from fastapi import APIRouter

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/")
def list_billing():
    return []
from fastapi import APIRouter

router = APIRouter(prefix="/billing")

@router.get("/")
async def list_billing():
    return {"billing": []}
