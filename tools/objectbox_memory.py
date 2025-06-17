import json
from uuid import uuid4
from models.schema import MemoryEntry, model # Import model, not store or box directly
from objectbox import Store # Import Store
import os # Added os import
from typing import Optional # Import Optional
import numpy as np # For cosine similarity calculation
from mycrews.qrew.tools.embed_and_store import embed_text # New import

# Define the default store path consistently with schema.py
_DEFAULT_STORE_PATH = ".db/objectbox"

class ObjectBoxMemory:
    _store = None # Class variable to hold the store instance
    _store_path = _DEFAULT_STORE_PATH # Class variable for store path, used by tests to override
    _current_store_actual_path = None # To store the actual path of the initialized store

    # _placeholder_embed function removed

    def __init__(self, store_path_override: Optional[str] = None): # Allow override
        current_path = store_path_override if store_path_override else self.__class__._store_path
        abs_current_path = os.path.abspath(current_path)

        if ObjectBoxMemory._store is None or ObjectBoxMemory._current_store_actual_path != abs_current_path:
            if ObjectBoxMemory._store:
                ObjectBoxMemory._store.close()
                ObjectBoxMemory._store = None

            parent_dir = os.path.dirname(abs_current_path) # Use abs_current_path for dirname
            if parent_dir:
                 os.makedirs(parent_dir, exist_ok=True)

            ObjectBoxMemory._store = Store(model=model, directory=abs_current_path)
            ObjectBoxMemory._current_store_actual_path = abs_current_path

        self.box = ObjectBoxMemory._store.box(MemoryEntry)

    @classmethod
    def close_store(cls):
        if cls._store:
            cls._store.close()
            cls._store = None
            cls._current_store_actual_path = None

    def save(self, value: str, metadata: Optional[dict] = None):
        if not value:
            return

        # raw_vec will be a np.ndarray from embed_text, or a zero vector if embed_text had issues
        raw_vec = embed_text(value)
        norm = np.linalg.norm(raw_vec)
        if norm == 0:
            vec = raw_vec # Already a zero vector or a valid non-normalizable vector
        else:
            vec = raw_vec / norm
        vec = vec.astype(np.float32) # Ensure correct dtype for storage

        meta_json = json.dumps(metadata or {})

        entry = MemoryEntry(
            id=0,
            content=value,
            vector=vec.tolist(), # Stored as list of floats
            metadata=meta_json,
        )
        self.box.put(entry)

    def query(self, query_text: str, limit: int = 5, score_threshold: float = 0.0) -> list[dict]:
        if not query_text:
            return []

        # raw_qvec will be a np.ndarray from embed_text, or a zero vector
        raw_qvec = embed_text(query_text)
        norm = np.linalg.norm(raw_qvec)
        if norm == 0:
            qvec = raw_qvec
        else:
            qvec = raw_qvec / norm
        qvec = qvec.astype(np.float32) # Ensure correct dtype

        if qvec is None or qvec.size == 0:
            print("Warning: Query vector is empty or embedding failed.") # Adjusted warning
            return []

        all_entries = self.box.get_all()
        if not all_entries:
            return []

        results_with_scores = []
        for entry in all_entries:
            if entry.vector is None: # Should not happen if save() is always used
                continue

            entry_vec = np.array(entry.vector, dtype=np.float32)

            # Assuming qvec and entry_vec are L2 normalized (embedder should handle this)
            # Cosine similarity = dot product for normalized vectors
            # Ensure entry_vec is also normalized if there's any doubt about stored vectors
            # For robustness, let's re-normalize entry_vec or use the full cosine similarity formula.
            # The embed() function in embedder.py is supposed to normalize.
            # So, we assume stored vectors are normalized.

            # Defensive check for zero vectors (if somehow stored or qvec is zero)
            qvec_norm = np.linalg.norm(qvec)
            entry_vec_norm = np.linalg.norm(entry_vec)

            if qvec_norm == 0 or entry_vec_norm == 0:
                similarity = 0.0
            else:
                # Standard cosine similarity formula for robustness,
                # though it simplifies to np.dot(qvec, entry_vec) if both are already unit vectors.
                similarity = np.dot(qvec, entry_vec) / (qvec_norm * entry_vec_norm)

            if similarity >= score_threshold:
                try:
                    metadata = json.loads(entry.metadata)
                except json.JSONDecodeError:
                    metadata = {} # Or some default error metadata
                results_with_scores.append({
                    "content": entry.content,
                    "metadata": metadata,
                    "score": similarity # Using "score" as per spec, higher is better
                })

        # Sort by score in descending order
        results_with_scores.sort(key=lambda x: x["score"], reverse=True)

        return results_with_scores[:limit]

    # _ensure_db_dir_exists was removed as it's not directly used by the class logic
    # and os.makedirs is handled in __init__.
    # The example call at the end was also removed as it's not part of the class.
