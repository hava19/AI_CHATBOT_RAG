from fastapi import APIRouter
from . import chat, ingest, health, admin

api_v1_router = APIRouter()
api_v1_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_v1_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_v1_router.include_router(health.router, prefix="/health", tags=["health"])
api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
