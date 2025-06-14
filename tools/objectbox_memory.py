import json
from uuid import uuid4
from models.schema import MemoryEntry, model # Import model, not store or box directly
from objectbox import Store # Import Store
import os # Added os import
from typing import Optional # Import Optional
from tools.embedder import embed

# Define the default store path consistently with schema.py
_DEFAULT_STORE_PATH = ".db/objectbox"

class ObjectBoxMemory:
    _store = None # Class variable to hold the store instance
    _store_path = _DEFAULT_STORE_PATH # Class variable for store path, used by tests to override
    _current_store_actual_path = None # To store the actual path of the initialized store

    def __init__(self, store_path_override: Optional[str] = None): # Allow override
        current_path = store_path_override if store_path_override else self.__class__._store_path
        abs_current_path = os.path.abspath(current_path)

        # Initialize store only if it hasn't been initialized or if the path has changed
        if ObjectBoxMemory._store is None or ObjectBoxMemory._current_store_actual_path != abs_current_path:
            if ObjectBoxMemory._store: # Close existing store if path changes
                ObjectBoxMemory._store.close()
                ObjectBoxMemory._store = None # Ensure it's reset

            # Ensure directory exists
            # Ensure parent directory of current_path exists, as ObjectBox creates the final directory component.
            parent_dir = os.path.dirname(current_path)
            if parent_dir: # Ensure parent_dir is not an empty string (e.g. if current_path is just "mydb")
                 os.makedirs(parent_dir, exist_ok=True)
            # If current_path itself is meant to be the directory containing db files (e.g. "path/to/db/")
            # then ObjectBox's `directory` parameter expects this path.
            # If current_path is "path/to/objectbox.db" (a file), dirname should be "path/to".
            # The Store() constructor expects the directory *containing* the database files.

            ObjectBoxMemory._store = Store(model=model, directory=abs_current_path) # Use abs_current_path
            ObjectBoxMemory._current_store_actual_path = abs_current_path # Store the path used

        self.box = ObjectBoxMemory._store.box(MemoryEntry)

    # Add a method to close the store, useful for testing
    @classmethod
    def close_store(cls):
        if cls._store:
            cls._store.close()
            cls._store = None
            cls._current_store_actual_path = None # Reset path on close

    def save(self, value: str, metadata: Optional[dict] = None):
        if not value:
            return

        # Embed the single value
        vec = embed([value])[0]
        meta_json = json.dumps(metadata or {})

        entry = MemoryEntry(
            id=0,  # ObjectBox assigns ID automatically if 0
            content=value,
            vector=vec.tolist(), # Ensure vector is a list of floats
            metadata=meta_json,
        )
        self.box.put(entry)

    def query(self, query_text: str, limit: int = 5, score_threshold: float = 0.0) -> list[dict]: # Adjusted signature to match Storage interface (limit, score_threshold)
        if not query_text:
            return []

        qvec = embed([query_text])[0] # Embedding will still be performed

        # --- HNSW Query robustly disabled ---
        # The entire try-except block for HNSW query is bypassed by returning early.
        return []
        # --- End HNSW Query robustly disabled ---

        # The following code becomes unreachable due to the return [] above.
        # results = []
        # try:
        #     # condition = MemoryEntry.vector.find_nearest_neighbors(qvec.tolist(), count=limit)
        #     # _query_obj = self.box.query(condition).build()
        #     # nearest_entities = _query_obj.find()
        #     # for entity in nearest_entities:
        #     #     results.append({
        #     #         "content": entity.content,
        #     #         "metadata": json.loads(entity.metadata),
        #     #         "distance": -1.0
        #     #     })
        #     # return [] # Original placement of temporary return
        # except Exception as e:
        #     print(f"Error during ObjectBox HNSW query (though it should be disabled): {e}")
        #     return []
        # return results

    def _ensure_db_dir_exists(self):
        # This is a helper that should ideally be called once at application startup.
        import os
        os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)

# Example of how the store directory could be ensured (e.g., in app main startup)
# ObjectBoxMemory()._ensure_db_dir_exists()
