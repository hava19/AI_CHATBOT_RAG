from fastapi import FastAPI
from .api.v1 import api_v1_router

app = FastAPI(title="AI Backend Enterprise")
app.include_router(api_v1_router, prefix="/api/v1")
