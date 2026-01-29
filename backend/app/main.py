from fastapi import FastAPI
from app.routers.sync import router as sync_router
from app.routers.health import router as health_router
from app.routers.albums import router as albums_router



app = FastAPI()

@app.get("/ping")
def ping():
    return {"ok": True}


app.include_router(health_router)
app.include_router(albums_router)
app.include_router(sync_router)
