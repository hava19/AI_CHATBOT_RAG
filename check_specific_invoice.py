#!/usr/bin/env python
"""
Script untuk cek detail invoice HID-1192141
"""

import asyncio
import sys
import re
sys.path.insert(0, '.')

async def check_invoice(invoice_number: str):
    from app.services.rag.vector_store import vector_store
    
    print(f"\n🔍 CEK DETAIL INVOICE: {invoice_number}")
    print("=" * 60)
    
    # Cari semua chunk dengan invoice ini
    results = vector_store.collection.get(limit=1000)
    
    if not results or not results['documents']:
        print("❌ Tidak ada data")
        return
    
    found_chunks = []
    amount_pattern = r'(?:IDR|Rp)[\s:]*([0-9,\.]+)'
    
    for i, (doc, meta, idx) in enumerate(zip(
        results['documents'],
        results['metadatas'] or [],
        results['ids'] or []
    )):
        if invoice_number in doc:
            amounts = re.findall(amount_pattern, doc)
            found_chunks.append({
                'id': idx,
                'content': doc,
                'metadata': meta,
                'amounts': amounts,
                'filename': meta.get('filename', 'unknown') if meta else 'unknown'
            })
    
    print(f"\n📊 Ditemukan {len(found_chunks)} chunk untuk {invoice_number}")
    
    for i, chunk in enumerate(found_chunks):
        print(f"\n--- Chunk {i+1} (file: {chunk['filename']}) ---")
        print(f"Amounts: {chunk['amounts']}")
        print(f"Preview: {chunk['content'][:300]}...")
        print(f"Metadata: {chunk['metadata']}")
    
    return found_chunks

if __name__ == "__main__":
    invoice = sys.argv[1] if len(sys.argv) > 1 else "HID-1192141"
    asyncio.run(check_invoice(invoice))