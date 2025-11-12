from fastapi import FastAPI
from .routes import __init__ as routes_pkg

app = FastAPI(title="Backend2 - Glenmore Wellness")

@app.get("/")
async def root():
    return {"status": "ok", "service": "backend2"}

# Include routers if any are defined in routes
try:
    for attr in dir(routes_pkg):
        obj = getattr(routes_pkg, attr)
        if hasattr(obj, "router"):
            app.include_router(obj.router)
except Exception:
    pass
