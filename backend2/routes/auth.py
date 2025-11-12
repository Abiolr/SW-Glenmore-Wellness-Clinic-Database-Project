from fastapi import APIRouter

router = APIRouter(prefix="/auth")

@router.post("/token")
async def token():
    return {"access_token": "dummy", "token_type": "bearer"}
