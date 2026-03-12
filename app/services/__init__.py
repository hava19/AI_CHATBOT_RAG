# DI Container
from .llm.openai_service import OpenAIService
from .embedding.openai_embedding import OpenAIEmbeddingService
from .rag.retriever import Retriever

llm_service = OpenAIService()
embedding_service = OpenAIEmbeddingService()
retriever = Retriever()

__all__ = ["llm_service", "embedding_service", "retriever"]
