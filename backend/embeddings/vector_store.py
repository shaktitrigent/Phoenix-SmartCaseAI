from typing import Dict, List, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import Config


class EmbeddingVectorStore:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or Config.EMBEDDING_MODEL_NAME
        self.model = None
        self.index = None
        self.metadata: List[Dict] = []
        self.enabled = True
        self._init_model()

    def _init_model(self):
        try:
            self.model = SentenceTransformer(self.model_name, local_files_only=True)
        except Exception:
            self.enabled = False

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        if not self.enabled or self.model is None:
            return
        cleaned = [t.strip() for t in texts if t and t.strip()]
        if not cleaned:
            return

        embeddings = self.model.encode(cleaned, convert_to_numpy=True)
        embeddings = embeddings.astype(np.float32)
        faiss.normalize_L2(embeddings)

        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        metadatas = metadatas or [{} for _ in cleaned]
        self.metadata.extend(
            [
                {"text": text, **meta}
                for text, meta in zip(cleaned, metadatas)
            ]
        )

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.enabled or self.model is None or self.index is None or not query.strip():
            return []
        vector = self.model.encode([query], convert_to_numpy=True).astype(np.float32)
        faiss.normalize_L2(vector)
        distances, indices = self.index.search(vector, top_k)
        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)
        return results
