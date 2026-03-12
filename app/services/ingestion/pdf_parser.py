"""
PDF Parser untuk ekstrak teks dari PDF
"""

from pypdf import PdfReader
from typing import List
import io

class PDFParser:
    async def parse(self, file_content: bytes) -> str:
        """
        Parse PDF file dan extract text
        """
        try:
            # Baca PDF dari bytes
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            # Extract text dari semua halaman
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    async def parse_with_metadata(self, file_content: bytes, filename: str) -> dict:
        """
        Parse PDF dan return dengan metadata
        """
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        
        # Extract text per halaman
        pages = []
        for i, page in enumerate(reader.pages):
            pages.append({
                'page_num': i + 1,
                'text': page.extract_text()
            })
        
        # Full text
        full_text = "\n".join([p['text'] for p in pages])
        
        return {
            'filename': filename,
            'num_pages': len(reader.pages),
            'full_text': full_text,
            'pages': pages,
            'metadata': reader.metadata
        }