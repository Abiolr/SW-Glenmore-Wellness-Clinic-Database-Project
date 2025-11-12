from fastapi import Request


async def auth_middleware(request: Request, call_next):
    # placeholder auth middleware
    response = await call_next(request)
    return response
from fastapi import Request

async def auth_middleware(request: Request, call_next):
    # placeholder authentication middleware
    response = await call_next(request)
    return response
