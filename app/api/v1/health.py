from fastapi import APIRouter
import subprocess
import os

router = APIRouter()

@router.get("/")
async def health_check():
    """
    Basic health check
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@router.get("/ollama")
async def ollama_health():
    """
    Cek koneksi ke Ollama
    """
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json()
                return {
                    "status": "connected",
                    "models": models
                }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)
        }

@router.get("/vectorstore")
async def vectorstore_health():
    """
    Cek vector store
    """
    try:
        from app.services.rag.vector_store import vector_store
        count = vector_store.collection.count()
        return {
            "status": "healthy",
            "total_chunks": count
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }