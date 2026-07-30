import os
from typing import List, Dict, Any, Optional
from src.app.config import settings

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None


class VectorStoreService:
    """Persistent Vector Database service wrapper powered by ChromaDB & sentence-transformers."""

    def __init__(self, collection_name: str = "blinkit_reviews"):
        self.collection_name = collection_name
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = None
        self.collection = None

        if chromadb:
            try:
                self.client = chromadb.PersistentClient(path=self.persist_dir)
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "Blinkit Customer Review Embeddings & Metadata"}
                )
            except Exception as e:
                print(f"VectorStoreService warning: Failed to initialize ChromaDB PersistentClient ({e})")

    def add_records(self, records: List[Dict[str, Any]]) -> int:
        """Upsert review records into the vector database.
        
        Each record should contain: 'id' or 'record_id', 'text' or 'clean_text', and optional metadata.
        """
        if not self.collection:
            print("VectorStoreService warning: ChromaDB collection is not active.")
            return 0

        ids = []
        documents = []
        metadatas = []

        for idx, rec in enumerate(records):
            doc_id = str(rec.get("id") or rec.get("record_id") or f"rec_{idx}")
            text = rec.get("clean_text") or rec.get("text") or rec.get("content") or ""
            if not text.strip():
                continue

            metadata = {
                "source": str(rec.get("source") or rec.get("channel") or "unknown"),
                "rating": int(rec.get("rating", 0)) if rec.get("rating") is not None else 0,
                "sentiment": str(rec.get("sentiment", "neutral")),
                "date": str(rec.get("date", "")),
            }

            ids.append(doc_id)
            documents.append(text)
            metadatas.append(metadata)

        if ids:
            # Batch upsert to prevent size limits
            batch_size = 500
            for i in range(0, len(ids), batch_size):
                self.collection.upsert(
                    ids=ids[i:i + batch_size],
                    documents=documents[i:i + batch_size],
                    metadatas=metadatas[i:i + batch_size],
                )
            return len(ids)
        return 0

    def search_similar(self, query_text: str, top_k: int = 10, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform semantic similarity search for a user query or theme topic."""
        if not self.collection:
            return []

        where_clause = {"source": source_filter} if source_filter else None
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_clause
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(docs)
            ids = results["ids"][0] if "ids" in results and results["ids"] else [""] * len(docs)
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(docs)

            for doc_id, doc, meta, dist in zip(ids, docs, metas, distances):
                formatted_results.append({
                    "id": doc_id,
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                    "similarity_score": round(1.0 / (1.0 + dist), 4) if dist is not None else None
                })

        return formatted_results

    def get_stats(self) -> Dict[str, Any]:
        """Return total collection count and storage info."""
        if not self.collection:
            return {"status": "inactive", "count": 0}
        return {
            "status": "active",
            "collection_name": self.collection_name,
            "count": self.collection.count(),
            "persist_dir": self.persist_dir,
        }
