"""
Text chunker untuk memecah dokumen jadi potongan kecil
"""

from typing import List
import re

class Chunker:
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):  # ← LEBIH KECIL!
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_by_sentences(self, text: str) -> List[str]:
        """
        Chunk berdasarkan kalimat dengan ukuran kecil
        """
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Kalau kalimat ini bikin chunk kebesaran, simpan dulu yang sekarang
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Overlap: ambil beberapa kalimat terakhir
                overlap_count = max(1, len(current_chunk) // 3)
                current_chunk = current_chunk[-overlap_count:]
                current_length = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add remaining
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        print(f"📊 Chunking: {len(sentences)} kalimat → {len(chunks)} chunks")
        return chunks
    
    def chunk_by_paragraphs(self, text: str) -> List[str]:
        """
        Chunk berdasarkan paragraf
        """
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        print(f"📊 Chunking by paragraph: {len(paragraphs)} paragraf → {len(chunks)} chunks")
        return chunks