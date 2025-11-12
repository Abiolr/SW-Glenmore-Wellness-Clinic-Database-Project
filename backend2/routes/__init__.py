"""Routes package for backend2"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["root"])
def root():
    return {"message": "backend2 routes root"}
"""Routes package - import routers here so main can auto-include them"""

from .patients import router as patients_router
from .staff import router as staff_router

# export common names
__all__ = ["patients_router", "staff_router"]
