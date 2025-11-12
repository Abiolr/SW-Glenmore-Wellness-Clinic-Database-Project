from fastapi import Request
import logging

logger = logging.getLogger("backend2")


async def logging_middleware(request: Request, call_next):
    logger.info("%s %s", request.method, request.url.path)
    response = await call_next(request)
    return response
import logging

logger = logging.getLogger("backend2")

async def logging_middleware(request, call_next):
    logger.info(f"{request.method} {request.url}")
    return await call_next(request)
