from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/ai"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Store - CHROMADB untuk development
    VECTOR_STORE_TYPE: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    
    # LLM - PAKAI OLLAMA!
    LLM_PROVIDER: str = "ollama"
    OLLAMA_HOST: str = "http://localhost:11434"
    # OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_MODEL: str ="qwen2.5:7b-instruct-q4_K_M"
    # OLLAMA_MODEL: str ="qwen2.5:1.5b-instruct"
    LOCAL_MODEL_PATH: str = "models/"
    
    # Embedding
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Untuk RAG
    # EMBEDDING_MODEL: str = "BAAI/bge-small-en"  # Untuk RAG
    
    # File upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()