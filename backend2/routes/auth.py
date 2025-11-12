from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login():
    return {"access_token": "fake-token"}
from fastapi import APIRouter

router = APIRouter(prefix="/auth")

@router.post("/token")
async def token():
    return {"access_token": "dummy", "token_type": "bearer"}
