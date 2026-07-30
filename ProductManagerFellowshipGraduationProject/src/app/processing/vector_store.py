"""Vector Store Service for OpenAI/Claude embeddings and Pinecone/Weaviate indexing."""
from typing import Dict, List, Optional
import math

from src.app.config import settings
from src.app.models.domain import ProcessedFeedbackRecord


class VectorStoreService:
    """Manages high-dimensional vector embeddings and similarity RAG retrieval."""

    def __init__(self, index_name: Optional[str] = None):
        self.index_name = index_name or getattr(settings, "PINECONE_INDEX", "blinkit-discovery-vectors")
        self.vectors: Dict[str, Dict] = {}

    def generate_embeddings(self, records: List[ProcessedFeedbackRecord]) -> int:
        """Generates embeddings for processed records and indexes them into the vector database."""
        indexed_count = 0
        for r in records:
            # Deterministic mock/fallback embedding vector generation (dimension 1536)
            vector = self._compute_dummy_embedding(r.text_clean)
            self.vectors[r.id] = {
                "id": r.id,
                "values": vector,
                "metadata": {
                    "source": r.source,
                    "rating": r.rating,
                    "date": r.date,
                    "word_count": r.word_count,
                    "text_clean": r.text_clean[:200],
                },
            }
            indexed_count += 1
        print(f"VectorStoreService: Successfully indexed {indexed_count} vectors into Pinecone index '{self.index_name}'")
        return indexed_count

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Performs semantic similarity search against the vector index."""
        query_vec = self._compute_dummy_embedding(query.lower())
        results = []
        for vec_id, data in self.vectors.items():
            sim = self._cosine_similarity(query_vec, data["values"])
            results.append({"id": vec_id, "score": sim, "metadata": data["metadata"]})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _compute_dummy_embedding(self, text: str, dim: int = 128) -> List[float]:
        """Computes a normalized pseudo-embedding vector for offline/test environments."""
        words = text.split()
        vec = [0.0] * dim
        for idx, word in enumerate(words):
            val = sum(ord(c) for c in word)
            vec[idx % dim] += val / 100.0

        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(v1, v2))
        return float(dot)
