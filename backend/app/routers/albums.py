from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["albums"])

@router.get("/albums")
def list_albums():
    return []
