"""
Embedding manager using sentence-transformers with simple on-disk cache.
"""
from typing import List, Iterable
import os
import pickle
import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_path: str = "embeddings_cache.pkl"):
        self.model = SentenceTransformer(model_name)
        self.cache_path = cache_path
        self._cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "rb") as fh:
                    return pickle.load(fh)
            except Exception:
                logger.exception("Failed to load embedding cache")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_path, "wb") as fh:
                pickle.dump(self._cache, fh)
        except Exception:
            logger.exception("Failed to save embedding cache")

    def embed_text(self, text: str) -> List[float]:
        if text in self._cache:
            return self._cache[text]
        emb = self.model.encode(text).tolist()
        self._cache[text] = emb
        self._save_cache()
        return emb

    def embed_batch(self, texts: Iterable[str], batch_size: int = 32):
        texts = list(texts)
        results = []
        to_compute = []
        to_compute_idx = []
        for i, t in enumerate(texts):
            if t in self._cache:
                results.append(self._cache[t])
            else:
                results.append(None)
                to_compute.append(t)
                to_compute_idx.append(i)
        if to_compute:
            emb_batch = self.model.encode(to_compute, batch_size=batch_size)
            for idx, emb in zip(to_compute_idx, emb_batch):
                self._cache[texts[idx]] = emb.tolist()
                results[idx] = emb.tolist()
            self._save_cache()
        return results