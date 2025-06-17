import os
import shutil # For cleaning up in tests if needed
import numpy as np
from objectbox import Store, Model
from objectbox.model import Entity, Id, Property # Corrected import for Property
import logging

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_STORE_PATH = "objectbox-data" # Default path for ONNX ObjectBox data

# --- Entity Definition ---
@Entity()
class KnowledgeEntry:
    id = Id()
    text = Property(str) # Property type is str
    embedding = Property(bytes) # Storing embedding as bytes
    project_id = Property(str) # Added project_id

def build_knowledge_entity_model(): # Renamed to be specific
    model = Model()
    model.entity(KnowledgeEntry)
    # It's important to call model.last_entity_id(last_id) and model.last_index_id(last_id)
    # if you've changed UIDs manually or are migrating. For a new model, this is fine.
    return model

class ONNXObjectBoxMemory:
    _store_instances = {} # Dictionary to hold store instances by path

    def __init__(self, store_path: str = DEFAULT_STORE_PATH):
        abs_store_path = os.path.abspath(store_path)
        self.store_path = abs_store_path

        if abs_store_path not in ONNXObjectBoxMemory._store_instances:
            self._ensure_db_dir_exists(abs_store_path)
            try:
                # Pass the model builder function directly
                store = Store(model=build_knowledge_entity_model(), directory=abs_store_path)
                ONNXObjectBoxMemory._store_instances[abs_store_path] = store
                logger.info(f"ObjectBox store initialized at {abs_store_path}")
            except Exception as e:
                logger.error(f"Failed to initialize ObjectBox store at {abs_store_path}: {e}")
                # Potentially re-raise or handle as a critical failure
                raise

        self.store = ONNXObjectBoxMemory._store_instances[abs_store_path]
        try:
            self.box = self.store.box(KnowledgeEntry)
        except Exception as e:
            logger.error(f"Failed to get box for KnowledgeEntry from store {abs_store_path}: {e}")
            # Potentially re-raise
            raise

    def _ensure_db_dir_exists(self, store_path: str):
        # For ObjectBox, store_path is the directory itself.
        # So we just need to ensure this directory exists.
        os.makedirs(store_path, exist_ok=True)


    def add_knowledge(self, text: str, vector: np.ndarray):
        if not isinstance(text, str) or not text.strip():
            logger.warning("Attempted to add empty or non-string text.")
            return
        if not isinstance(vector, np.ndarray):
            logger.warning("Attempted to add non-NumPy array vector.")
            return

        entry = KnowledgeEntry()
        entry.text = text
        entry.embedding = vector.astype(np.float32).tobytes() # Ensure float32 and store as bytes

        try:
            self.box.put(entry)
            # logger.debug(f"Added knowledge: '{text[:50]}...'")
        except Exception as e:
            logger.error(f"Failed to add knowledge for text '{text[:50]}...': {e}")


    def vector_query(self, query_vector: np.ndarray, limit: int = 3, score_threshold: float = 0.7) -> list[dict]: # Increased score_threshold to 0.7
        if not isinstance(query_vector, np.ndarray):
            logger.warning("Query vector is not a NumPy array.")
            return []
        if query_vector.size == 0:
            logger.warning("Query vector is empty.")
            return []

        scored_results = []
        try:
            all_entries = self.box.get_all()
            if not all_entries:
                # logger.debug("No entries found in the database for vector query.")
                return []

            q_vec_norm = np.linalg.norm(query_vector)
            if q_vec_norm == 0:
                logger.warning("Query vector norm is zero, cannot compute similarity.")
                return []

            for entry in all_entries:
                if entry.embedding is None or len(entry.embedding) == 0:
                    # logger.debug(f"Skipping entry ID {entry.id} with missing embedding.")
                    continue

                entry_vec = np.frombuffer(entry.embedding, dtype=np.float32)
                entry_vec_norm = np.linalg.norm(entry_vec)

                if entry_vec_norm == 0:
                    # logger.debug(f"Skipping entry ID {entry.id} with zero-norm stored vector.")
                    continue

                # Cosine similarity
                similarity = np.dot(query_vector, entry_vec) / (q_vec_norm * entry_vec_norm)

                if similarity >= score_threshold: # Apply threshold
                    scored_results.append({
                        "content": entry.text,
                        "score": float(similarity) # Ensure score is standard float
                    })

            # Sort by score in descending order
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            # logger.debug(f"Vector query processed {len(all_entries)} entries, found {len(scored_results)} matches, returning top {limit}.")
            return scored_results[:limit]

        except Exception as e:
            logger.error(f"Error during vector query: {e}")
            return []

    @classmethod
    def close_store_instance(cls, store_path: str = DEFAULT_STORE_PATH): # Renamed for clarity
        abs_store_path = os.path.abspath(store_path)
        if abs_store_path in cls._store_instances:
            try:
                cls._store_instances[abs_store_path].close()
                del cls._store_instances[abs_store_path]
                logger.info(f"ObjectBox store closed for path: {abs_store_path}")
            except Exception as e:
                logger.error(f"Error closing ObjectBox store for path {abs_store_path}: {e}")
        else:
            logger.info(f"No active store instance found for path to close: {abs_store_path}")

    @classmethod
    def remove_store_files(cls, store_path: str = DEFAULT_STORE_PATH):
        """For cleaning up test databases. Ensures the store is closed before removal."""
        abs_store_path = os.path.abspath(store_path)
        # Attempt to close the store instance if it's managed by this class
        if abs_store_path in cls._store_instances:
            cls.close_store_instance(abs_store_path)

        # Now, remove the directory
        if os.path.exists(abs_store_path):
            try:
                shutil.rmtree(abs_store_path)
                logger.info(f"Removed store directory: {abs_store_path}")
            except OSError as e:
                logger.error(f"Error removing store directory {abs_store_path}: {e}. It might be in use if not closed properly by all holders.")
        else:
            logger.info(f"Store directory not found (already removed or never existed): {abs_store_path}")
