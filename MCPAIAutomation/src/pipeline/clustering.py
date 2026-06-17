from typing import List, Dict, Any, Optional
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA

logger = logging.getLogger(__name__)

class ClusteringPipeline:
    def __init__(self, min_reviews: int = 20, random_state: int = 42, 
                 openai_api_key: Optional[str] = None, hf_token: Optional[str] = None, 
                 config: Optional[Any] = None):
        self.min_reviews = min_reviews
        self.random_state = random_state
        self.openai_api_key = openai_api_key
        self.hf_token = hf_token
        self.config = config

        # Set default parameters or read from config
        self.umap_n_neighbors = 15
        self.umap_n_components = 5
        self.umap_metric = "cosine"
        self.hdbscan_min_cluster_size = 5
        self.hdbscan_min_samples = 3

        if config and hasattr(config, "pipeline") and hasattr(config.pipeline, "clustering"):
            c_conf = config.pipeline.clustering
            if hasattr(c_conf, "umap"):
                self.umap_n_neighbors = getattr(c_conf.umap, "n_neighbors", 15)
                self.umap_n_components = getattr(c_conf.umap, "n_components", 5)
                self.umap_metric = getattr(c_conf.umap, "metric", "cosine")
            if hasattr(c_conf, "hdbscan"):
                self.hdbscan_min_cluster_size = getattr(c_conf.hdbscan, "min_cluster_size", 5)
                self.hdbscan_min_samples = getattr(c_conf.hdbscan, "min_samples", 3)

    def _get_hf_embeddings(self, texts: List[str]) -> np.ndarray:
        """Retrieves text embeddings from Hugging Face Inference API (BAAI/bge-small-en-v1.5)."""
        if not self.hf_token:
            raise ValueError("Hugging Face API token (HF_TOKEN) is missing.")
            
        import urllib.request
        import json
        
        url = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-small-en-v1.5"
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        batch_size = 64
        if self.config and hasattr(self.config, "pipeline") and hasattr(self.config.pipeline, "embedding"):
            batch_size = getattr(self.config.pipeline.embedding, "batch_size", 64)
            
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            data = json.dumps({"inputs": batch, "options": {"wait_for_model": True}}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req) as res:
                    response_data = json.loads(res.read().decode("utf-8"))
                    all_embeddings.extend(response_data)
            except Exception as e:
                logger.error(f"Hugging Face Inference API error on batch {i}: {e}")
                raise e
                
        return np.array(all_embeddings)

    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Retrieves text embeddings from OpenAI API."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is missing.")
            
        from openai import OpenAI
        client = OpenAI(api_key=self.openai_api_key)
        
        batch_size = 64
        if self.config and hasattr(self.config, "pipeline") and hasattr(self.config.pipeline, "embedding"):
            batch_size = getattr(self.config.pipeline.embedding, "batch_size", 64)
            
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = client.embeddings.create(
                input=batch,
                model="text-embedding-3-small"
            )
            embeddings = [d.embedding for d in response.data]
            all_embeddings.extend(embeddings)
            
        return np.array(all_embeddings)

    def run(self, reviews: List[Any], num_clusters: int = 5) -> List[Dict[str, Any]]:
        """
        Clusters a list of reviews.
        Aborts if the count of unique reviews is less than min_reviews.
        Returns a list of cluster dictionaries sorted by score descending.
        """
        n_reviews = len(reviews)
        if n_reviews < self.min_reviews:
            raise ValueError(
                f"Review count ({n_reviews}) is below the minimum required ({self.min_reviews}) to run clustering."
            )

        # Extract texts and ratings safely
        texts = []
        ratings = []
        for r in reviews:
            if isinstance(r, dict):
                text = r.get("text", "")
                rating = r.get("rating") if "rating" in r else r.get("score")
            else:
                text = getattr(r, "text", "")
                rating = getattr(r, "rating", None)
                if rating is None:
                    rating = getattr(r, "score", None)
            texts.append(str(text))
            ratings.append(int(rating) if rating is not None else 3)

        # 2. Get dense/sparse representations
        embeddings = None
        
        provider = "openai"
        if self.config and hasattr(self.config, "pipeline") and hasattr(self.config.pipeline, "embedding"):
            provider = getattr(self.config.pipeline.embedding, "provider", "openai").lower()
            
        if provider == "huggingface" or (self.hf_token and not self.openai_api_key):
            try:
                embeddings = self._get_hf_embeddings(texts)
                logger.info("Hugging Face BGE-small embeddings generated successfully.")
            except Exception as e:
                logger.warning(f"Hugging Face embedding retrieval failed: {e}. Trying OpenAI fallback.")

        if embeddings is None and self.openai_api_key:
            try:
                embeddings = self._get_embeddings(texts)
                logger.info("OpenAI embeddings generated successfully.")
            except Exception as e:
                logger.warning(f"OpenAI embedding retrieval failed: {e}. Falling back to TF-IDF.")

        # Fallback to TF-IDF if embeddings failed/were disabled
        if embeddings is None:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
            embeddings = vectorizer.fit_transform(texts).toarray()
            logger.info("TF-IDF vector representation generated.")

        # 3. Dimensionality Reduction
        reduced_matrix = None
        # Try UMAP
        try:
            import umap
            reducer = umap.UMAP(
                n_neighbors=self.umap_n_neighbors,
                n_components=self.umap_n_components,
                metric=self.umap_metric,
                random_state=self.random_state
            )
            reduced_matrix = reducer.fit_transform(embeddings)
            logger.info("UMAP reduction executed successfully.")
        except (ImportError, Exception) as e:
            logger.info(f"UMAP reduction not available/failed: {e}. Falling back to PCA.")
            
        # Fallback to PCA if UMAP failed/missing
        if reduced_matrix is None:
            n_components = min(self.umap_n_components, embeddings.shape[1], embeddings.shape[0])
            reducer = PCA(n_components=n_components, random_state=self.random_state)
            reduced_matrix = reducer.fit_transform(embeddings)
            logger.info("PCA reduction executed.")

        # 4. Clustering (Try HDBSCAN, fallback to KMeans)
        labels = None
        try:
            clusterer = HDBSCAN(
                min_cluster_size=self.hdbscan_min_cluster_size,
                min_samples=self.hdbscan_min_samples,
                metric="euclidean"
            )
            labels = clusterer.fit_predict(reduced_matrix)
            logger.info("HDBSCAN clustering executed.")
        except Exception as e:
            logger.warning(f"HDBSCAN clustering failed: {e}. Falling back to KMeans.")

        # Evaluate if HDBSCAN succeeded or found only noise (-1)
        unique_labels = set(labels) if labels is not None else set()
        non_noise_labels = [l for l in unique_labels if l != -1]
        
        # Fallback to KMeans if HDBSCAN failed or returned purely noise
        if not non_noise_labels:
            logger.info("HDBSCAN produced no valid clusters. Falling back to KMeans.")
            k = min(num_clusters, len(reviews))
            k = max(2, k)
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = kmeans.fit_predict(reduced_matrix)
            logger.info(f"KMeans clustering executed (K={k}).")

        # Group reviews by cluster label
        clusters_data = {}
        for idx, label in enumerate(labels):
            # Treat noise label -1 as a distinct cluster or filter it out?
            # Standard clustering report expects us to classify even noise/residuals if needed,
            # or treat them as a "Miscellaneous" cluster. Here we keep it as a cluster,
            # but rank it appropriately.
            label_id = int(label)
            if label_id not in clusters_data:
                clusters_data[label_id] = {
                    "cluster_id": label_id,
                    "reviews": [],
                    "ratings": []
                }
            clusters_data[label_id]["reviews"].append(reviews[idx])
            clusters_data[label_id]["ratings"].append(ratings[idx])

        # Calculate scores and build final cluster representation
        ranked_clusters = []
        for label_id, data in clusters_data.items():
            cluster_reviews = data["reviews"]
            cluster_ratings = data["ratings"]
            avg_rating = float(np.mean(cluster_ratings))
            size = len(cluster_reviews)
            
            # Score = Size * (6 - Average Rating)
            # If noise cluster (-1), reduce its score priority
            if label_id == -1:
                score = size * (6.0 - avg_rating) * 0.1
            else:
                score = size * (6.0 - avg_rating)
            
            ranked_clusters.append({
                "cluster_id": label_id,
                "reviews": cluster_reviews,
                "score": score,
                "avg_rating": avg_rating,
                "size": size
            })

        # Sort clusters by score descending
        ranked_clusters.sort(key=lambda c: c["score"], reverse=True)
        return ranked_clusters

