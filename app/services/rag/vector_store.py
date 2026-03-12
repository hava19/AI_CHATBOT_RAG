"""
Vector store service untuk RAG
Menggunakan ChromaDB dengan optimasi untuk pencarian invoice dan manajemen duplikat
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import uuid
import re
import hashlib
from datetime import datetime
from collections import defaultdict
from app.core.config import settings

class VectorStore:
    def __init__(self):
        # Inisialisasi ChromaDB
        persist_dir = settings.CHROMA_PERSIST_DIR or "./data/chroma"
        print(f"📁 ChromaDB persist dir: {persist_dir}")
        
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Buat atau dapatkan collection
        try:
            self.collection = self.client.get_collection("company_documents")
            count = self.collection.count()
            print(f"✅ Collection exists, total chunks: {count}")
            
            # Tampilkan sample metadata untuk debugging
            if count > 0:
                sample = self.collection.get(limit=1)
                if sample and sample['metadatas']:
                    print(f"📊 Sample metadata: {sample['metadatas'][0]}")
                    
        except Exception as e:
            self.collection = self.client.create_collection(
                name="company_documents",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Collection created")
    
    # ======================================================
    # METHOD 1: ADD DOCUMENT DENGAN METADATA LENGKAP
    # ======================================================
    async def add_document(
        self,
        doc_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict]] = None
    ):
        """
        Tambah dokumen ke vector store dengan metadata yang diperkaya
        """
        try:
            # VALIDASI
            if not chunks or len(chunks) == 0:
                print("❌ Error: No chunks to add")
                return 0
            
            if len(chunks) != len(embeddings):
                print(f"❌ Error: Mismatch chunks ({len(chunks)}) and embeddings ({len(embeddings)})")
                return 0
            
            # Generate IDs
            ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
            
            # PERKAYA METADATA
            enriched_metadata = []
            invoice_pattern = r'[A-Z]+[-]?\d+'
            
            for i, (chunk, meta) in enumerate(zip(chunks, metadata or [{}] * len(chunks))):
                # Base metadata dengan info versi
                enriched = {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "upload_timestamp": datetime.now().isoformat(),
                    **meta  # Merge dengan metadata yang diberikan
                }
                
                # Ekstrak nomor invoice dari chunk
                found_invoices = re.findall(invoice_pattern, chunk)
                if found_invoices:
                    enriched["contains_invoice"] = True
                    enriched["invoice_numbers"] = ",".join(found_invoices[:5])  # Max 5 invoice per chunk
                    print(f"   🔍 Chunk {i} contains invoices: {found_invoices[:3]}")
                
                # Deteksi keyword penting
                text_lower = chunk.lower()
                if "total" in text_lower or "jumlah" in text_lower or "harga" in text_lower:
                    enriched["contains_total"] = True
                if "tanggal" in text_lower or "date" in text_lower or "jatuh tempo" in text_lower:
                    enriched["contains_date"] = True
                if "client" in text_lower or "customer" in text_lower or "pelanggan" in text_lower:
                    enriched["contains_client"] = True
                
                enriched_metadata.append(enriched)
            
            # Add ke ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=enriched_metadata,
                ids=ids
            )
            
            print(f"✅ Successfully added {len(chunks)} chunks with enriched metadata")
            
            # Statistik
            invoice_chunks = sum(1 for m in enriched_metadata if m.get("contains_invoice"))
            total_chunks = sum(1 for m in enriched_metadata if m.get("contains_total"))
            print(f"📊 Stats: {invoice_chunks} chunks contain invoices, {total_chunks} contain totals")
            
            return len(chunks)
            
        except Exception as e:
            print(f"❌ Error adding document: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    # ======================================================
    # METHOD 2: CHECK DUPLIKAT SMART
    # ======================================================
    
    async def check_duplicate_smart(
        self, 
        filename: str, 
        file_hash: str,
        file_size: int
    ) -> Dict:
        """
        Cek duplikat dengan logika pintar
        - File identik (hash sama) → reject
        - File beda isi tapi nama sama → tanya user (replace/new version)
        """
        try:
            # Cari semua chunks dengan filename ini
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if not results or not results['documents']:
                return {
                    "is_duplicate": False,
                    "action": "new",
                    "message": "File baru, silakan upload"
                }
            
            # Kumpulkan info dari metadata
            existing_versions = []
            file_hashes = set()
            
            for meta in results['metadatas'] or []:
                if meta:
                    doc_id = meta.get('doc_id')
                    
                    # Cek apakah doc_id ini sudah tercatat
                    existing = next(
                        (v for v in existing_versions if v['doc_id'] == doc_id), 
                        None
                    )
                    
                    if not existing:
                        existing_versions.append({
                            'doc_id': doc_id,
                            'version': meta.get('version', 1),
                            'timestamp': meta.get('upload_timestamp'),
                            'file_hash': meta.get('file_hash'),
                            'is_latest': meta.get('is_latest', False)
                        })
                    
                    if meta.get('file_hash'):
                        file_hashes.add(meta.get('file_hash'))
            
            # Logic decision
            if file_hash in file_hashes:
                # File identik sudah ada
                return {
                    "is_duplicate": True,
                    "action": "reject",
                    "message": "File sudah pernah diupload dengan isi yang sama",
                    "existing_versions": existing_versions
                }
            
            # File dengan nama sama tapi isi berbeda
            return {
                "is_duplicate": True,
                "action": "ask_user",
                "message": "File dengan nama sama sudah ada, tapi isinya berbeda",
                "options": ["replace", "new_version", "cancel"],
                "existing_versions": existing_versions
            }
            
        except Exception as e:
            print(f"❌ Error checking duplicate: {e}")
            return {"is_duplicate": False, "error": str(e)}
    
    # ======================================================
    # METHOD 3: GET FILE VERSIONS
    # ======================================================
    async def get_file_versions(self, filename: str) -> List[Dict]:
        """
        Dapatkan semua versi file berdasarkan nama
        """
        results = self.collection.get(
            where={"filename": filename}
        )
        
        if not results or not results['metadatas']:
            return []
        
        versions = {}
        for meta in results['metadatas']:
            if meta:
                doc_id = meta.get('doc_id')
                if doc_id not in versions:
                    versions[doc_id] = {
                        'doc_id': doc_id,
                        'timestamp': meta.get('upload_timestamp'),
                        'chunks': 0,
                        'file_hash': meta.get('file_hash'),
                        'version': meta.get('version', 1),
                        'is_latest': meta.get('is_latest', False)
                    }
                versions[doc_id]['chunks'] += 1
        
        # Urutkan berdasarkan timestamp (terbaru dulu)
        return sorted(
            versions.values(),
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
    
    # ======================================================
    # METHOD 4: HANDLE DUPLICATE UPLOAD
    # ======================================================
    async def handle_duplicate_upload(
        self,
        old_doc_id: str,
        new_doc_id: str,
        action: str,  # "replace" atau "new_version"
        new_version_number: int = None
    ) -> Dict:
        """
        Handle duplikat sesuai pilihan user
        """
        try:
            if action == "replace":
                # Hapus dokumen lama
                await self.delete_document(old_doc_id)
                
                # Update metadata dokumen baru sebagai latest
                results = self.collection.get(
                    where={"doc_id": new_doc_id}
                )
                
                if results and results['ids']:
                    # ChromaDB tidak support update metadata massal
                    # Kita akan handle via ingest.py dengan version info
                    pass
                
                return {
                    "action": "replaced",
                    "message": "Dokumen lama diganti dengan yang baru"
                }
                
            elif action == "new_version":
                # Update versi dokumen baru
                results = self.collection.get(
                    where={"doc_id": new_doc_id}
                )
                
                if results and results['metadatas']:
                    # Versi sudah di-set di ingest.py
                    pass
                
                return {
                    "action": "new_version",
                    "message": f"Disimpan sebagai versi {new_version_number}"
                }
            
            elif action == "cancel":
                return {
                    "action": "cancelled",
                    "message": "Upload dibatalkan"
                }
                
            return {
                "action": "unknown",
                "message": "Tidak ada tindakan yang dilakukan"
            }
                
        except Exception as e:
            print(f"❌ Error handling duplicate: {e}")
            return {"error": str(e)}
    
    # ======================================================
    # METHOD 5: REMOVE DUPLICATES BY FILENAME
    # ======================================================
    async def remove_duplicates_by_filename(
        self, 
        filename: str, 
        keep_newest: bool = True
    ) -> Dict:
        """
        Hapus duplikat berdasarkan nama file
        """
        try:
            # Cari semua chunk dengan filename tertentu
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if not results or not results['documents']:
                return {"message": f"File {filename} tidak ditemukan", "deleted": 0}
            
            # Kelompokkan berdasarkan doc_id
            doc_groups = defaultdict(list)
            
            for i, (doc, meta, idx) in enumerate(zip(
                results['documents'],
                results['metadatas'] or [],
                results['ids'] or []
            )):
                if meta:
                    doc_id = meta.get('doc_id', 'unknown')
                    doc_groups[doc_id].append({
                        'id': idx,
                        'chunk_index': meta.get('chunk_index', 0),
                        'timestamp': meta.get('upload_timestamp', ''),
                        'content': doc[:100]
                    })
            
            # Jika hanya 1 group, tidak ada duplikat
            if len(doc_groups) <= 1:
                return {
                    "message": f"Tidak ada duplikat untuk {filename}",
                    "deleted": 0,
                    "groups": len(doc_groups)
                }
            
            # Pilih group yang akan disimpan
            if keep_newest:
                # Cari group dengan timestamp terbaru
                best_group = max(
                    doc_groups.items(), 
                    key=lambda x: max(
                        (c['timestamp'] for c in x[1] if c['timestamp']), 
                        default=''
                    )
                )[0]
            else:
                # Simpan group dengan chunks terbanyak
                best_group = max(doc_groups.items(), key=lambda x: len(x[1]))[0]
            
            # Hapus group lainnya
            deleted_count = 0
            deleted_ids = []
            
            for doc_id, chunks in doc_groups.items():
                if doc_id != best_group:
                    ids_to_delete = [c['id'] for c in chunks]
                    self.collection.delete(ids=ids_to_delete)
                    deleted_count += len(ids_to_delete)
                    deleted_ids.extend(ids_to_delete)
                    print(f"   🗑️ Menghapus {len(ids_to_delete)} chunks dari doc_id {doc_id}")
            
            return {
                "message": f"Berhasil menghapus duplikat untuk {filename}",
                "deleted": deleted_count,
                "deleted_ids": deleted_ids[:10],  # Preview 10 ids
                "kept_doc_id": best_group,
                "total_groups": len(doc_groups)
            }
            
        except Exception as e:
            print(f"❌ Error removing duplicates: {e}")
            return {"error": str(e)}
    
    # ======================================================
    # METHOD 6: AUTO CLEANUP ALL DUPLICATES
    # ======================================================
    async def auto_cleanup_duplicates(self, strategy: str = "keep_newest") -> Dict:
        """
        Auto cleanup semua duplikat di database
        strategy: "keep_newest", "keep_largest"
        """
        try:
            # Dapatkan semua filename unik
            all_chunks = self.collection.get(limit=10000)
            filenames = set()
            
            for meta in all_chunks.get('metadatas', []):
                if meta and meta.get('filename'):
                    filenames.add(meta.get('filename'))
            
            print(f"\n🔍 Menemukan {len(filenames)} file unik")
            
            total_deleted = 0
            cleanup_results = []
            
            for filename in filenames:
                print(f"\n📄 Memproses: {filename}")
                result = await self.remove_duplicates_by_filename(
                    filename=filename,
                    keep_newest=(strategy == "keep_newest")
                )
                
                if 'deleted' in result:
                    total_deleted += result['deleted']
                    if result['deleted'] > 0:
                        cleanup_results.append({
                            'filename': filename,
                            'deleted': result['deleted'],
                            'kept': result.get('kept_doc_id')
                        })
            
            return {
                'status': 'success',
                'strategy': strategy,
                'total_deleted': total_deleted,
                'files_cleaned': len(cleanup_results),
                'details': cleanup_results[:20]  # Max 20 detail
            }
            
        except Exception as e:
            print(f"❌ Error auto cleanup: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # ======================================================
    # METHOD 7: LIST ALL DOCUMENTS
    # ======================================================
    async def list_all_documents(self) -> List[Dict]:
        """
        Dapatkan daftar semua dokumen (unique by filename)
        """
        try:
            # Ambil semua chunks
            results = self.collection.get(limit=10000)
            
            if not results or not results['documents']:
                return []
            
            # Kelompokkan berdasarkan filename
            docs = defaultdict(lambda: {
                'doc_ids': set(),
                'chunks': 0,
                'first_seen': None,
                'last_seen': None,
                'invoices': set(),
                'versions': set()
            })
            
            for meta in results['metadatas'] or []:
                if meta:
                    filename = meta.get('filename', 'unknown')
                    doc_id = meta.get('doc_id', 'unknown')
                    timestamp = meta.get('upload_timestamp', '')
                    version = meta.get('version', 1)
                    
                    docs[filename]['doc_ids'].add(doc_id)
                    docs[filename]['chunks'] += 1
                    docs[filename]['versions'].add(version)
                    
                    if meta.get('invoice_numbers'):
                        invoices = meta['invoice_numbers'].split(',')
                        docs[filename]['invoices'].update(invoices)
                    
                    # Track first and last seen
                    if not docs[filename]['first_seen'] or timestamp < docs[filename]['first_seen']:
                        docs[filename]['first_seen'] = timestamp
                    if not docs[filename]['last_seen'] or timestamp > docs[filename]['last_seen']:
                        docs[filename]['last_seen'] = timestamp
            
            # Format hasil
            result = []
            for filename, data in docs.items():
                result.append({
                    'filename': filename,
                    'versions': len(data['doc_ids']),
                    'version_numbers': sorted(data['versions']),
                    'total_chunks': data['chunks'],
                    'doc_ids': list(data['doc_ids']),
                    'invoices': list(data['invoices'])[:10],  # Max 10 invoice preview
                    'first_seen': data['first_seen'],
                    'last_seen': data['last_seen'],
                    'is_duplicate': len(data['doc_ids']) > 1
                })
            
            return sorted(result, key=lambda x: x['filename'])
            
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            return []
    
    # ======================================================
    # METHOD 8: SEARCH BY INVOICE
    # ======================================================
    async def search_by_invoice(
        self,
        invoice_number: str,
        top_k: int = 5,
        debug: bool = True
    ) -> List[Dict]:
        """
        Cari spesifik berdasarkan nomor invoice
        - Prioritas 1: Exact match via metadata
        - Prioritas 2: Exact match di content
        - Prioritas 3: Semantic search
        """
        results = []
        
        if debug:
            print(f"\n🔍 SEARCHING INVOICE: {invoice_number}")
            print("=" * 60)
        
        # METHOD 1: Exact match via metadata
        try:
            metadata_results = self.collection.get(
                where={"invoice_numbers": {"$contains": invoice_number}}
            )
            
            if metadata_results and metadata_results['documents']:
                if debug:
                    print(f"✅ METHOD 1: Found {len(metadata_results['documents'])} exact metadata matches")
                
                for i in range(len(metadata_results['documents'])):
                    results.append({
                        'content': metadata_results['documents'][i],
                        'metadata': metadata_results['metadatas'][i] if metadata_results['metadatas'] else {},
                        'id': metadata_results['ids'][i] if metadata_results['ids'] else None,
                        'match_type': 'exact_metadata',
                        'relevance': 1.0
                    })
        except Exception as e:
            if debug:
                print(f"⚠️ Metadata search error: {e}")
        
        # METHOD 2: Jika belum cukup, cari di content
        if len(results) < top_k:
            try:
                # Ambil semua chunks (limit 100 untuk performance)
                all_chunks = self.collection.get(limit=100)
                
                if all_chunks and all_chunks['documents']:
                    for i, doc in enumerate(all_chunks['documents']):
                        if invoice_number in doc:
                            results.append({
                                'content': doc,
                                'metadata': all_chunks['metadatas'][i] if all_chunks['metadatas'] else {},
                                'id': all_chunks['ids'][i] if all_chunks['ids'] else None,
                                'match_type': 'exact_content',
                                'relevance': 0.95
                            })
                            
                            if debug:
                                print(f"✅ METHOD 2: Found exact match in content")
            except Exception as e:
                if debug:
                    print(f"⚠️ Content search error: {e}")
        
        # METHOD 3: Semantic search sebagai fallback
        if len(results) == 0:
            if debug:
                print(f"⚠️ No exact matches, trying semantic search...")
            
            # Panggil search biasa
            semantic_results = await self.search(
                query_text=f"invoice nomor {invoice_number} total harga jumlah",
                top_k=top_k,
                debug=debug
            )
            
            for r in semantic_results:
                r['match_type'] = 'semantic'
                r['relevance'] = 1 - r.get('distance', 0)
                results.append(r)
        
        # DEDUPLIKASI
        seen = set()
        unique_results = []
        for r in results:
            content_hash = hash(r['content'][:100])
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(r)
        
        # SORT by relevance
        unique_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        if debug:
            print(f"\n📊 FINAL RESULTS: {len(unique_results)} unique chunks")
            for i, r in enumerate(unique_results[:3]):
                print(f"\n--- Result {i+1} (type: {r['match_type']}, relevance: {r.get('relevance', 0):.2f}) ---")
                print(f"Content: {r['content'][:200]}...")
        
        return unique_results[:top_k]
    
    # ======================================================
    # METHOD 9: SEARCH (GENERAL)
    # ======================================================
    async def search(
        self,
        query_embedding: Optional[List[float]] = None,
        query_text: Optional[str] = None,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None,
        debug: bool = False
    ) -> List[Dict]:
        """
        Enhanced search dengan filter dan debug option
        """
        try:
            if debug:
                print(f"\n🔍 SEARCHING VECTOR STORE")
                if query_text:
                    print(f"   Query text: {query_text[:100]}...")
                if filter_dict:
                    print(f"   Filter: {filter_dict}")
            
            # Jika ada query_text tapi tidak ada embedding, kita perlu embed dulu
            if query_text and not query_embedding:
                from app.services.embedding.sentence_transformer import embedding_service
                query_embedding = await embedding_service.embed(query_text)
            
            # Prepare query parameters
            query_params = {
                "query_embeddings": [query_embedding] if query_embedding else None,
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"]
            }
            
            if filter_dict:
                query_params["where"] = filter_dict
            
            # Execute query
            if query_embedding:
                results = self.collection.query(**query_params)
            else:
                # Jika tidak ada query embedding, ambil random
                results = self.collection.get(limit=top_k)
            
            documents = []
            if results and results.get('documents') and results['documents'][0]:
                if debug:
                    print(f"✅ Found {len(results['documents'][0])} results")
                
                for i in range(len(results['documents'][0])):
                    doc = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                        'distance': results['distances'][0][i] if results.get('distances') else None,
                        'relevance': 1 - results['distances'][0][i] if results.get('distances') else 0.5
                    }
                    
                    # Tambah info invoice jika ada
                    if doc['metadata'].get('contains_invoice'):
                        doc['invoice_numbers'] = doc['metadata'].get('invoice_numbers', '')
                    
                    documents.append(doc)
                    
                    if debug and i == 0:
                        print(f"   Top result: {doc['content'][:100]}...")
                        if doc['metadata']:
                            print(f"   Metadata: {doc['metadata']}")
            else:
                if debug:
                    print("❌ No results found")
            
            return documents
            
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []
    
    # ======================================================
    # METHOD 10: HYBRID SEARCH
    # ======================================================
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        prefer_exact: bool = True
    ) -> List[Dict]:
        """
        Hybrid search: gabungkan exact match dan semantic search
        """
        # Cek apakah query mengandung nomor invoice
        invoice_pattern = r'[A-Z]+[-]?\d+'
        mentioned_invoices = re.findall(invoice_pattern, query)
        
        results = []
        
        # Jika ada nomor invoice, prioritaskan exact match
        if mentioned_invoices and prefer_exact:
            for inv in mentioned_invoices:
                inv_results = await self.search_by_invoice(inv, top_k=3, debug=False)
                results.extend(inv_results)
        
        # Jika belum cukup, tambah dengan semantic search
        if len(results) < top_k:
            from app.services.embedding.sentence_transformer import embedding_service
            query_embedding = await embedding_service.embed(query)
            semantic_results = await self.search(
                query_embedding=query_embedding,
                top_k=top_k - len(results),
                debug=False
            )
            results.extend(semantic_results)
        
        # Deduplikasi
        seen = set()
        unique_results = []
        for r in results:
            content_hash = hash(r['content'][:200])
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(r)
        
        return unique_results[:top_k]
    
    # ======================================================
    # METHOD 11: GET INVOICE SUMMARY
    # ======================================================
    async def get_invoice_summary(self) -> Dict:
        """
        Dapatkan ringkasan semua invoice di database
        """
        try:
            # Ambil semua chunks yang mengandung invoice
            results = self.collection.get(
                where={"contains_invoice": True},
                limit=1000
            )
            
            if not results or not results['documents']:
                return {"total_invoices": 0, "invoice_numbers": []}
            
            # Ekstrak semua nomor invoice
            all_invoices = set()
            for metadata in results['metadatas'] or []:
                if metadata and metadata.get('invoice_numbers'):
                    invoices = metadata['invoice_numbers'].split(',')
                    all_invoices.update(invoices)
            
            return {
                "total_chunks_with_invoice": len(results['documents']),
                "unique_invoices": list(all_invoices)[:50],  # Max 50
                "total_unique_invoices": len(all_invoices)
            }
            
        except Exception as e:
            print(f"❌ Error getting invoice summary: {e}")
            return {"error": str(e)}
    
    # ======================================================
    # METHOD 12: DELETE DOCUMENT
    # ======================================================
    async def delete_document(self, doc_id: str):
        """
        Hapus dokumen berdasarkan ID
        """
        try:
            # Cari semua chunk dengan doc_id
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"✅ Deleted document {doc_id} ({len(results['ids'])} chunks)")
            else:
                print(f"⚠️ Document {doc_id} not found")
                
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
    
    # ======================================================
    # METHOD 13: GET COLLECTION STATS
    # ======================================================
    def get_collection_stats(self) -> Dict:
        """
        Dapatkan statistik lengkap collection
        """
        try:
            count = self.collection.count()
            
            # Sample metadata untuk analisis
            invoice_count = 0
            duplicate_files = 0
            
            if count > 0:
                sample = self.collection.get(limit=100)
                if sample and sample['metadatas']:
                    invoice_count = sum(
                        1 for m in sample['metadatas'] 
                        if m and m.get('contains_invoice')
                    )
                    
                    # Cek duplikat file
                    filenames = {}
                    for m in sample['metadatas']:
                        if m and m.get('filename'):
                            fname = m.get('filename')
                            if fname in filenames:
                                duplicate_files += 1
                            else:
                                filenames[fname] = True
            
            return {
                "status": "healthy",
                "total_chunks": count,
                "collection_name": "company_documents",
                "invoice_chunks_sample": invoice_count,
                "duplicate_files_sample": duplicate_files,
                "persist_directory": settings.CHROMA_PERSIST_DIR
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# ======================================================
# SINGLETON INSTANCE
# ======================================================
vector_store = VectorStore()