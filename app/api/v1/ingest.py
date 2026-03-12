"""
Endpoint untuk upload dan proses dokumen internal perusahaan
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.services.ingestion.pdf_parser import PDFParser
from app.services.ingestion.chunker import Chunker
from app.services.embedding.sentence_transformer import embedding_service
from app.services.rag.vector_store import vector_store
from app.core.config import settings
import uuid
import os
from typing import List
import asyncio

router = APIRouter()
pdf_parser = PDFParser()
chunker = Chunker(chunk_size=500, chunk_overlap=100)

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # ... validasi ...
    
    doc_id = str(uuid.uuid4())
    content = await file.read()
    
    # Simpan sementara
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    temp_path = f"{settings.UPLOAD_DIR}/{doc_id}_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(content)
    
    # Proses dengan chunking yang lebih baik
    background_tasks.add_task(
        process_document_improved,
        doc_id=doc_id,
        file_content=content,
        filename=file.filename,
        temp_path=temp_path
    )
    
    return {
        "message": "Dokumen sedang diproses dengan chunking optimal",
        "document_id": doc_id,
        "filename": file.filename,
        "status": "processing"
    }

async def process_document_improved(
    doc_id: str,
    file_content: bytes,
    filename: str,
    temp_path: str
):
    """
    Improved document processing dengan chunking lebih baik
    """
    try:
        print(f"\n🔍 MEMPROSES DOKUMEN: {filename}")
        print("=" * 50)
        
        # 1. Parse PDF
        from app.services.ingestion.pdf_parser import PDFParser
        parser = PDFParser()
        text = await parser.parse(file_content)
        
        if not text or len(text.strip()) == 0:
            print("❌ Error: PDF kosong atau tidak bisa diekstrak")
            return
            
        print(f"✅ PDF parsed: {len(text)} characters")
        print(f"   Preview: {text[:200]}...")
        
        # 2. Chunk text
        from app.services.ingestion.chunker import Chunker
        chunker = Chunker(chunk_size=300, chunk_overlap=50)
        
        chunks = chunker.chunk_by_sentences(text)
        print(f"✅ Chunking result: {len(chunks)} chunks")
        
        # VALIDASI: Pastikan chunks tidak kosong
        if not chunks or len(chunks) == 0:
            print("❌ Error: No chunks generated")
            return
        
        # 3. Generate embeddings
        from app.services.embedding.sentence_transformer import embedding_service
        embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"   🔢 Generating embedding for chunk {i+1}/{len(chunks)}")
            try:
                embedding = await embedding_service.embed(chunk)
                embeddings.append(embedding)
                print(f"      Embedding length: {len(embedding)}")
            except Exception as e:
                print(f"      ❌ Error embedding chunk {i}: {e}")
                continue
        
        # VALIDASI: Pastikan embeddings tidak kosong
        if not embeddings or len(embeddings) == 0:
            print("❌ Error: No embeddings generated")
            return
        
        # 4. Save to vector store
        from app.services.rag.vector_store import vector_store
        result = await vector_store.add_document(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=[{
                "filename": filename,
                "chunk_index": i,
                "doc_id": doc_id,
                "chunk_size": len(chunk)
            } for i, chunk in enumerate(chunks)]
        )
        
        if result > 0:
            print(f"\n✅ DOKUMEN BERHASIL DIPROSES!")
            print(f"📊 Statistik:")
            print(f"   - Total chunks: {len(chunks)}")
            print(f"   - Total embeddings: {len(embeddings)}")
            print(f"   - Document ID: {doc_id}")
        else:
            print(f"\n❌ GAGAL menyimpan ke vector store")
        
        # Hapus file sementara
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"🗑️ File sementara dihapus")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
async def process_document_background(
    doc_id: str,
    file_content: bytes,
    filename: str,
    temp_path: str
):
    """
    Background task untuk proses dokumen
    - Parse PDF
    - Chunk text
    - Generate embeddings
    - Simpan di vector store
    """
    try:
        print(f"🔍 Memproses dokumen: {filename} (ID: {doc_id})")
        
        # 1. Parse PDF
        text = await pdf_parser.parse(file_content)
        print(f"✅ PDF parsed: {len(text)} characters")
        
        # 2. Chunk text
        chunks = chunker.chunk_by_sentences(text, sentences_per_chunk=5)
        print(f"✅ Text chunked: {len(chunks)} chunks")
        
        # 3. Generate embeddings for chunks
        embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"   Generating embedding for chunk {i+1}/{len(chunks)}")
            embedding = await embedding_service.embed(chunk)
            embeddings.append(embedding)
        
        # 4. Simpan di vector store
        await vector_store.add_document(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=[{
                "filename": filename,
                "chunk_index": i,
                "doc_id": doc_id
            } for i in range(len(chunks))]
        )
        
        print(f"✅ Dokumen selesai diproses: {len(chunks)} chunks disimpan")
        
        # Hapus file sementara (optional)
        os.remove(temp_path)
        
    except Exception as e:
        print(f"❌ Error processing document: {str(e)}")

@router.get("/status/{doc_id}")
async def get_status(doc_id: str):
    """
    Cek status pemrosesan dokumen
    """
    # TODO: Implementasi status tracking
    return {
        "document_id": doc_id,
        "status": "completed"  # Sementara
    }