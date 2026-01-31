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

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BACKEND_DIR = Path(__file__).resolve().parents[1]          # .../backend
FRONTEND_DIST = BACKEND_DIR.parent / "frontend" / "dist"  # .../frontend/dist

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="ui")

    # fallback SPA (para rutas del front)
    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            # si alguien pegó mal una ruta /api, que devuelva 404 real
            return {"detail": "Not Found"}
        return FileResponse(str(FRONTEND_DIST / "index.html"))
