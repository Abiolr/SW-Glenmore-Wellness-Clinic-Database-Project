from fastapi import Request


async def rbac_middleware(request: Request, call_next):
    # placeholder role-based access control
    response = await call_next(request)
    return response
def check_role(role: str):
    def _inner():
        # placeholder RBAC
        return True
    return _inner
