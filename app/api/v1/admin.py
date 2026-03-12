from fastapi import APIRouter
router = APIRouter()

@router.get("/admin/stats")
async def admin_stats():
    return {"stats": {}}
