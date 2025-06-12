# crewAI SQLite Integration & Refactoring Plan
Generated: 2025-06-07 10:24:57

This document outlines a plan to adapt `crewai` for improved Termux compatibility, focusing on replacing `chromadb` with a user-provided SQLite-based vector storage solution and addressing the `onnxruntime` dependency.

## 1. Integrating SQLite-based Vector Storage (Alternative to ChromaDB)

The user cannot install `chromadb` on their Termux environment and has provided a Python `Database` class using SQLite and NumPy for basic vector storage and similarity search. This section details how `crewai` currently uses `chromadb` and proposes a strategy to integrate the user's solution.

### 1.1. Current `chromadb` Usage in `crewai`
Analysis of `src/crewai/knowledge/storage/knowledge_storage.py`, `src/crewai/memory/storage/rag_storage.py`, and `src/crewai/utilities/embedding_configurator.py` reveals the following `chromadb` API usage:
- **Client:** `chromadb.PersistentClient(path=...)` is used to create on-disk vector stores.
- **Collections:** `app.get_or_create_collection(name=..., embedding_function=...)`, `app.get_collection(...)`, `app.create_collection(...)` are used. Collections are named based on knowledge base names or memory types.
- **Embedding Functions:** `EmbeddingConfigurator` is used to supply `chromadb` with an appropriate `EmbeddingFunction` (e.g., OpenAI, Ollama), which `chromadb` then uses internally to convert text to vectors during `add`/`upsert`/`query`.
- **Data Operations:**
  - `KnowledgeStorage`: Uses `collection.upsert(documents=List[str], metadatas=List[Optional[Dict]], ids=List[str])`. IDs are content hashes.
  - `RAGStorage`: Uses `collection.add(documents=[text], metadatas=[metadata], ids=[uuid_str])`. IDs are random UUIDs.
- **Querying:** `collection.query(query_texts=Union[str, List[str]], n_results=int, where=Optional[Dict])`. The `where` clause allows metadata-based filtering.
- **Management:** `app.reset()` for clearing storage.

### 1.2. Mapping to User's `Database` Class & Identified Gaps
The user's `Database` class provides methods like `store_embedding(item_id, agent_id, role, content, embedding)` and `retrieve_similar_items(query_embedding, top_k)`. Key differences and gaps when mapping to `crewai`'s needs:
1.  **Embedding Generation:** User's class expects pre-computed embeddings. `crewai` (with `chromadb`) relies on the `embedding_function` within `chromadb` to do this. **Solution:** The new adapter must explicitly generate embeddings before calling the user's `store_embedding` or `retrieve_similar_items` (for query texts).
2.  **Collection Management:** User's class has a single 'memory' table. `crewai` uses named collections. **Solution:** The user's `Database` class needs to be modified or wrapped to handle multiple tables (one per `crewai` collection) or use a single table with a `collection_name` column for differentiation.
3.  **Metadata Storage:** User's `store_embedding` has fixed `agent_id`, `role` fields. `crewai` uses a flexible `metadata` dictionary. **Solution:** User's table schema needs a TEXT column (e.g., `metadata_json`) to store the JSON string of `crewai`'s metadata dictionary.
4.  **Query Filtering (`where` clause):** User's `retrieve_similar_items` does not support metadata filtering. This is a CRITICAL feature for effective RAG. **Solution:** The `retrieve_similar_items` method in the user's `Database` class needs significant enhancement to parse a filter dictionary and construct dynamic SQL `WHERE` clauses (potentially using SQLite's `json_extract` for the `metadata_json` column).
5.  **Search Scalability & Performance:** User's current similarity search loads all embeddings and computes similarity in Python. This will be slow for large datasets. `chromadb` uses indexed vector search (e.g., HNSW). **Note:** This is an inherent performance difference. The SQLite solution will be less performant for large N. Consider this a known trade-off for Termux compatibility with smaller datasets.
6.  **Query Input:** `KnowledgeStorage.search` can take a list of query texts. User's `retrieve_similar_items` takes a single query embedding. **Solution:** The adapter should loop if multiple query texts are provided.

### 1.3. Proposed Integration Strategy: Abstract `VectorStoreInterface`
To integrate the SQLite solution cleanly, `crewai` should use an abstraction layer for vector storage.
1.  **Define `VectorStoreInterface` (ABC):**
    ```python
    from abc import ABC, abstractmethod
    from typing import List, Dict, Any, Optional, Union

    class VectorStoreQueryResult: # Define structure for query results
        # Example attributes, adjust as per actual chromadb query results structure
        # ids: List[str]
        # documents: Optional[List[Optional[str]]]
        # metadatas: Optional[List[Optional[Dict[str, Any]]]]
        # distances: Optional[List[Optional[float]]]
        # Usually, chromadb returns lists of lists for these if multiple queries are made.
        # For a single query's results, it might be List[Dict] or similar.
        # For this interface, let's assume a simplified result per queried item for now.
        id: str
        document: Optional[str] # Changed from context for clarity
        metadata: Optional[Dict[str, Any]]
        distance: Optional[float] # Changed from score for clarity (lower is better)

        def __init__(self, id: str, document: Optional[str], metadata: Optional[Dict[str, Any]], distance: Optional[float]):
            self.id = id
            self.document = document
            self.metadata = metadata
            self.distance = distance

    class VectorStoreInterface(ABC):
        @abstractmethod
        def __init__(self, collection_name: str, embedder_config: Optional[Dict[str, Any]] = None, persist_path: Optional[str] = None, **kwargs):
            # self.embedding_model = EmbeddingConfigurator().configure_embedder(embedder_config) # This line needs careful thought
            # EmbeddingConfigurator returns an EmbeddingFunction for Chroma, not a raw model.
            # The interface might need direct access to an embedding generation function/method.
            pass

        @abstractmethod
        def add(self, documents: List[str], metadatas: Optional[List[Optional[Dict[str, Any]]]] = None, ids: Optional[List[str]] = None) -> None:
            pass

        @abstractmethod
        def search(self, query_texts: List[str], n_results: int = 5, filter_criteria: Optional[Dict[str, Any]] = None) -> List[List[VectorStoreQueryResult]]:
            # Returns a list of lists, one inner list per query_text
            pass

        @abstractmethod
        def reset(self) -> None:
            pass
    ```
2.  **Refactor `KnowledgeStorage` & `RAGStorage`:** Modify them to accept and use an instance of `VectorStoreInterface` via dependency injection.
3.  **Create `ChromaDBVectorStore(VectorStoreInterface)`:** Adapts existing `chromadb` logic to this interface. It will manage its own `chromadb.PersistentClient` and `EmbeddingFunction` (via `EmbeddingConfigurator`).
4.  **Create `SQLiteVectorStore(VectorStoreInterface)`:**
    - Wraps the user's (enhanced) `Database` class.
    - **Initialization:** Takes `collection_name` (becomes table name), `embedder_config` (to get an embedding model for explicit embedding generation, likely from `EmbeddingConfigurator` which needs adjustment to provide a direct embedding function).
    - **`add` method:**
        1. Uses an embedding model (derived from `embedder_config`) to get embeddings for input `documents`.
        2. Calls user's `Database.store_embedding` (enhanced for table name and full metadata JSON).
    - **`search` method:**
        1. Uses the embedding model to get embeddings for input `query_texts`.
        2. Calls user's `Database.retrieve_similar_items` (enhanced for table name and metadata filtering).
        3. Formats results to `List[List[VectorStoreQueryResult]]`.
5.  **Enhance User's `Database` Class:**
    - Modify `__init__` to accept `db_path` and `table_name`. Ensure the table exists with schema: `item_id TEXT PRIMARY KEY, content TEXT, embedding BLOB, metadata_json TEXT`.
    - Modify `store_embedding` to use `table_name` and accept `metadata: Dict[str, Any]` (serialize to JSON). Implement `UPSERT` logic using `item_id`.
    - CRITICAL: Modify `retrieve_similar_items` to use `table_name` and accept `filter_criteria: Dict[str, Any]`. Implement dynamic SQL `WHERE` clause generation using SQLite's `json_extract` on `metadata_json` column. For example: `SELECT item_id, content, metadata_json, embedding FROM {table_name} WHERE json_extract(metadata_json, '$.source') = ?`.
6.  **Configuration Update:** `crewai`'s main configuration (e.g., in `Crew` or `KnowledgeBase`) needs to allow specifying the vector store implementation and its specific configuration (like `db_path` for SQLite, `persist_path` for ChromaDB).
    - `EmbeddingConfigurator` will need to be adaptable to provide either a `chromadb.EmbeddingFunction` or a more direct embedding generation callable for the SQLite adapter.

## 2. Addressing `onnxruntime` Dependency

- **Status:** `onnxruntime` is a core dependency in `crewai`'s `pyproject.toml` but is unavailable in the user's Termux environment.
- **Observation:** No direct Python imports of `onnxruntime` were found in `src/crewai`. This suggests indirect usage (e.g., by a dependency of `crewai` like `tokenizers` or `litellm` under certain configurations) or dynamic loading.
- **Challenge:** Without knowing how/where `crewai`'s functionality might trigger `onnxruntime` (possibly through `litellm` for specific embedding models or local model inference), pinpointing exact refactoring points is difficult.
- **Recommendations:**
  1.  **Audit Usage:** `crewai` maintainers or the user should investigate why `onnxruntime` is a core dependency. Is it tied to specific embedding models in `litellm` or other features? `litellm` documentation mentions ONNX for certain local embedding models.
  2.  **Conditional Logic for Features:** If `onnxruntime` is used for specific, non-default features (e.g., certain local embedding models), ensure these features are wrapped in `try-except ImportError` blocks within `crewai` or its dependencies (like `EmbeddingConfigurator` if it tries to load an ONNX-based embedder).
  3.  **Graceful Degradation:** If `onnxruntime` is not found, affected features should be disabled, and the user should be informed (e.g., warning log, or functions returning a specific status indicating unavailability). For instance, if an ONNX-based embedder fails to load, `EmbeddingConfigurator` should fall back to another available model or raise a clear error.
  4.  **Reclassify Dependency (if applicable):** If `onnxruntime` is only for optional features (e.g., specific local embedding models not used by default), `crewai` maintainers could consider moving it to an optional dependency group (e.g., `crewai[onnx-embeddings]`). This seems like the most viable path if its usage is confirmed to be optional.
  5.  **User Action:** The user should ensure their `litellm` configuration (if they customize it for `crewai`) does not select embedding models or features that require `onnxruntime` if they cannot install it.

## 3. Next Steps

### For User:
1.  **Enhance `Database` Class:** Implement the changes detailed in section 1.3 (Point 5), focusing on table creation with the new schema, `UPSERT` for `store_embedding`, and robust metadata filtering in `retrieve_similar_items` using `json_extract`.
2.  **Test `Database` Class:** Thoroughly test the enhanced `Database` class standalone with sample data and queries, especially the metadata filtering.

### For `crewai` (or User's Fork thereof):
1.  **Implement `VectorStoreInterface`:** Define the ABC as proposed in section 1.3 (Point 1).
2.  **Create `ChromaDBVectorStore` Adapter:** Wrap existing `chromadb` usage into this new interface (section 1.3, Point 3).
3.  **Create `SQLiteVectorStore` Adapter:** Implement this adapter to use the user's enhanced `Database` class and a direct embedding generation mechanism (section 1.3, Point 4). This will involve adjusting `EmbeddingConfigurator` to provide a callable for direct embedding generation if it doesn't already.
4.  **Refactor Storage Classes:** Modify `KnowledgeStorage` and `RAGStorage` to use `VectorStoreInterface` through dependency injection.
5.  **Configuration Mechanism:** Implement a way for `crewai` to select and configure the desired `VectorStoreInterface` implementation at runtime (e.g., based on a config object passed to `Crew` or `KnowledgeBase`).
6.  **Investigate `onnxruntime`:** Determine its exact role. If confirmed optional or for specific embedders, move to an optional dependency group in `pyproject.toml` and ensure `EmbeddingConfigurator` handles its absence gracefully.
7.  **Testing:** Add unit and integration tests for the new interface, both adapters, and the refactored storage classes.
