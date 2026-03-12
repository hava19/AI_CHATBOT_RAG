#!/usr/bin/env python
"""
Script untuk upload banyak PDF sekaligus
"""

import asyncio
import httpx
import os
from pathlib import Path

async def upload_pdf(file_path: str, api_url: str = "http://localhost:8000/api/v1/ingest/upload"):
    """
    Upload single PDF
    """
    filename = Path(file_path).name
    
    with open(file_path, 'rb') as f:
        files = {'file': (filename, f, 'application/pdf')}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                files=files,
                headers={"X-API-Key": "test123"}  # Sesuaikan dengan auth Anda
            )
            
            if response.status_code == 200:
                print(f"✅ {filename}: {response.json()}")
                return response.json()
            else:
                print(f"❌ {filename}: {response.text}")
                return None

async def upload_folder(folder_path: str):
    """
    Upload semua PDF dalam folder
    """
    pdf_files = list(Path(folder_path).glob("*.pdf"))
    print(f"Menemukan {len(pdf_files)} file PDF")
    
    for pdf_file in pdf_files:
        await upload_pdf(str(pdf_file))
        await asyncio.sleep(1)  # Jeda antar upload

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python bulk_upload.py <folder_path>")
        sys.exit(1)
    
    folder = sys.argv[1]
    asyncio.run(upload_folder(folder))