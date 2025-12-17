"""
FAISS vector store wrapper with metadata support (simple).
"""
from typing import List, Dict, Any, Optional
import faiss
import numpy as np
import os
import pickle
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, dim: int, index_path: str = "faiss.index", meta_path: str = "faiss_meta.pkl"):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = faiss.IndexFlatL2(dim)
        self._metadatas: List[Dict[str, Any]] = []
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.load()

    def add(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        arr = np.array(embeddings).astype("float32")
        if arr.ndim == 1:
            arr = np.expand_dims(arr, 0)
        self.index.add(arr)
        self._metadatas.extend(metadatas)

    def search(self, query_emb: List[float], top_k: int = 5, metadata_filter: Optional[Dict[str, Any]] = None):
        q = np.array([query_emb]).astype("float32")
        D, I = self.index.search(q, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            meta = self._metadatas[idx]
            if metadata_filter:
                ok = all(meta.get(k) == v for k, v in metadata_filter.items())
                if not ok:
                    continue
            results.append({"score": float(dist), "metadata": meta, "index": int(idx)})
        return results

    def save(self):
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.meta_path, "wb") as fh:
                pickle.dump(self._metadatas, fh)
        except Exception:
            logger.exception("Failed to save FAISS index")

    def load(self):
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as fh:
                self._metadatas = pickle.load(fh)
        except Exception:
            logger.exception("Failed to load FAISS store")