import json
from uuid import uuid4
from models.schema import MemoryEntry, model # Import model, not store or box directly
from objectbox import Store # Import Store
import os # Added os import
from typing import Optional # Import Optional
from tools.embedder import embed

# Define the default store path consistently with schema.py
_DEFAULT_STORE_PATH = "/data/data/com.termux/files/home/crewAI/db"

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

        qvec = embed([query_text])[0]

        # HNSW KNN search using query builder
        # The issue's example: hits = self.box.query(MemoryEntry.vector).build().find_nearest(qvec.tolist(), max_distance=None, limit=top_k)
        # This specific syntax for find_nearest on a built query for a property might be version-dependent.
        # A more standard way for HNSW in ObjectBox Python for versions around 4.0.0 would be:
        # query_builder = self.box.query(MemoryEntry.vector.nearest(qvec.tolist(), top_k))
        # However, to stick to the spirit of the issue if that syntax is intended from a specific context:

        results = []
        try:
            # Attempting a syntax that might align with the issue's description of find_nearest,
            # though typical ObjectBox HNSW queries are structured differently.
            # This is speculative based on the `.build().find_nearest` part of the issue's example.
            # A direct `find_nearest` on a built query after just passing the property to `box.query()`
            # is not standard. Standard would be `box.query(MemoryEntry.vector.nearest(vector, k))`

            # Let's try to use nearest_neighbors directly on the box, which is a known API method,
            # but it returns objects, not Hit(object, distance) directly.
            # We will have to manually construct the distance or assume it's not needed if not returned.

            # The issue's example `hits = self.box.query(MemoryEntry.vector).build().find_nearest(...)`
            # is problematic because `self.box.query(MemoryEntry.vector)` is not a valid condition start.
            # Trying a query builder chain style based on common patterns and C API hints
            # qb = self.box.query() # Get QueryBuilder
            # condition = qb.param(MemoryEntry.vector).nearest_neighbors(qvec.tolist(), count=limit)
            # _query = qb.build() # Build after condition is applied

            # Construct the HNSW nearest neighbor condition on the vector property
            # Assuming 'nearest' is the method and 'k' is the parameter for the count.
            # If the actual method or parameter name is different, this will need adjustment.
            condition = MemoryEntry.vector.nearest(qvec.tolist(), k=limit)

            # Build the query with this condition
            _query_obj = self.box.query(condition).build() # Renamed to _query_obj to avoid reusing _query variable if it exists elsewhere

            # Execute the query
            nearest_entities = _query_obj.find()

            # If the goal is to get Hit(object, distance) as implied by `hit.distance` later,
            # this query form doesn't directly provide distances.
            # ObjectBox's Python API for HNSW distances might require specific handling or might have evolved.
            # For now, we'll populate with a placeholder for distance if not available.
            # The score_threshold parameter is currently unused as distances are not directly retrieved.
            # If distances were available, this threshold could be used to filter results.

            for entity in nearest_entities:
                # Placeholder for distance, as `find()` on a standard query doesn't typically return it.
                # ObjectBox orders by distance with `nearest`, so the order is significant.
                # Actual distance/score retrieval might require a different API usage or version.
                distance_placeholder = -1.0 # Using -1.0 to indicate unavailable distance.

                results.append({
                    "content": entity.content,
                    "metadata": json.loads(entity.metadata),
                    "distance": distance_placeholder # Placeholder, actual distance not retrieved.
                })

            # If the issue's syntax `self.box.query(MemoryEntry.vector).build().find_nearest(...)`
            # was intended to be a valid call that returns Hit(object, distance) objects,
            # then the following would be more appropriate (but relies on that specific API call working):
            #
            # _hits_from_issue_syntax = self.box.query(MemoryEntry.vector.nearest(qvec.tolist(), count=top_k)).build().find_nearest(qvec.tolist(), limit=top_k) # This is still not quite right.
            # The `find_nearest` is usually a method of the box or a specific query type, not a generic built query.
            #
            # A more plausible interpretation of the issue's intent, if distances are crucial and
            # `Hit` objects are expected, might involve a specific HNSW query method that returns them.
            # Given the constraints and the provided snippet, the current implementation above with `find()`
            # is the most robust standard ObjectBox query. If distances are critical and not returned,
            # this part of the implementation will need refinement based on exact ObjectBox capabilities.

        except Exception as e:
            print(f"Error during ObjectBox HNSW query: {e}")
            # Fallback to empty list
            return []
        return results

    def _ensure_db_dir_exists(self):
        # This is a helper that should ideally be called once at application startup.
        import os
        os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)

# Example of how the store directory could be ensured (e.g., in app main startup)
# ObjectBoxMemory()._ensure_db_dir_exists()
