import logging

logger = logging.getLogger("backend2")

async def logging_middleware(request, call_next):
    logger.info(f"{request.method} {request.url}")
    return await call_next(request)
