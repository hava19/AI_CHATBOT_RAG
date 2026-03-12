"""
Chat endpoint dengan RAG (Retrieval Augmented Generation)
Bisa bertanya tentang dokumen internal perusahaan
"""

from fastapi import APIRouter, HTTPException, Depends
from app.services.llm.ollama_service import OllamaService
from app.services.embedding.sentence_transformer import embedding_service
from app.services.rag.vector_store import vector_store
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.security import verify_api_key
from typing import Optional

router = APIRouter()

# Initialize services
llm_service = OllamaService()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Chat dengan AI Assistant yang bisa menjawab pertanyaan
    berdasarkan dokumen internal perusahaan
    """
    try:
        # 1. Generate embedding untuk query
        query_embedding = await embedding_service.embed(request.message)
        
        # 2. Cari dokumen relevan di vector store
        relevant_docs = await vector_store.search(
            query_embedding=query_embedding,
            top_k=5
        )
        
        # 3. Buat context dari dokumen yang ditemukan
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # 4. Buat prompt dengan context
        system_prompt = f"""Kamu adalah Malih AI Assistant.
                            Asisten virtual resmi PT HJM
                            yang dibuat oleh Hadi .
                            PT HJM bergerak dalam bidang transportasi laut , peminjaman kontainer
                            Jawab profesional dan fokus pada konteks perusahaan.
                            Jika tidak tahu, katakan tidak tersedia.

                            CONTEXT:
                            {context}

                            Jawab dengan bahasa Indonesia yang baik dan benar.
                            """
        
        # 5. Generate response dari LLM
        response = await llm_service.generate(
            prompt=request.message,
            system_prompt=system_prompt,
            temperature=0.3  # Lebih rendah untuk lebih fokus ke context
        )
        
        # 6. Return response dengan sumber (optional)
        return ChatResponse(
            message=response,
            conversation_id=request.conversation_id,
            sources=[doc['metadata'] for doc in relevant_docs]  # Tambah field ini
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Streaming version of chat with RAG
    """
    from fastapi.responses import StreamingResponse
    
    async def generate():
        try:
            # 1. Generate embedding
            query_embedding = await embedding_service.embed(request.message)
            
            # 2. Search relevant docs
            relevant_docs = await vector_store.search(
                query_embedding=query_embedding,
                top_k=5
            )
            
            # 3. Build context
            context = "\n\n".join([doc['content'] for doc in relevant_docs])
            
            # 4. Stream response
            system_prompt = f"""Gunakan context berikut untuk menjawab:
{context}"""
            
            async for chunk in llm_service.generate_stream(
                prompt=request.message,
                system_prompt=system_prompt,
                temperature=0.3
            ):
                yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )