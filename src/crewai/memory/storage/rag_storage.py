import logging
import uuid
from typing import Any, Dict, List, Optional

from crewai.memory.storage.base_rag_storage import BaseRAGStorage
# Vector Store Interface and implementations
from crewai.vectorstores.base import (VectorStoreInterface,
                                     VectorStoreQueryResult)
from crewai.vectorstores.sqlite_store import SQLiteVectorStore as ChromaDBVectorStore

logger = logging.getLogger(__name__)

class RAGStorage(BaseRAGStorage):
    """
    Handles storage and retrieval of embeddings for memory entries using a
    configurable vector store backend, improving search efficiency.
    """

    vector_store: Optional[VectorStoreInterface] = None

    def __init__(
        self,
        storage_config: Dict[str, Any], # e.g., {"type": "sqlite", "collection_name": "my_rag", "persist_path": "/path/to/db"}
        embedder_config: Optional[Dict[str, Any]] = None,
        crew=None # crew object might be used for context, e.g. agent names for collection naming
    ):
        # The 'type' argument for super() was for the memory type (e.g., 'short_term'),
        # now collection_name is primary.
        # We can derive a default collection_name if not in storage_config.
        collection_name_from_config = storage_config.get("collection_name", "default_rag_collection")

        # The original __init__ used 'type' (e.g. short_term_memory) as the collection name.
        # We pass this 'type' (now collection_name_from_config) to super if it expects it.
        # The BaseRAGStorage __init__ was: def __init__(self, type, allow_reset=True, embedder_config=None, crew=None):
        # Let's assume the 'type' for BaseRAGStorage is informational and can be the collection_name.
        super().__init__(type=collection_name_from_config, embedder_config=embedder_config, crew=crew)

        self.storage_config = storage_config
        self.embedder_config = embedder_config # Stored by superclass as well

        # The collection name for the vector store will be primarily from storage_config
        self.collection_name = collection_name_from_config

        # The original RAGStorage used agent names to make storage_file_name unique.
        # This responsibility should now ideally be part of the `persist_path` or `collection_name`
        # logic when defining storage_config if such uniqueness per crew is needed.
        # For now, we'll rely on collection_name from storage_config for uniqueness.
        # If `crew` object is passed, it could be used to further refine collection_name or persist_path if needed.
        # Example: self.collection_name = self._get_effective_collection_name(crew)

        self._initialize_vector_store()


    def _initialize_vector_store(self):
        """Initializes the vector store based on the provided configuration."""
        store_type = self.storage_config.get("type", "chromadb").lower()
        # Use self.collection_name which might have been refined by __init__ logic
        collection_name = self.collection_name
        persist_path = self.storage_config.get("persist_path")

        logger.info(
            f"Initializing RAG vector store: type='{store_type}', collection='{collection_name}', persist_path='{persist_path}'"
        )

        if store_type == "sqlite":
            self.vector_store = SQLiteVectorStore(
                collection_name=collection_name,
                embedder_config=self.embedder_config, # self.embedder_config is set by super().__init__
                persist_path=persist_path,
            )
        elif store_type == "chromadb":
            self.vector_store = ChromaDBVectorStore(
                collection_name=collection_name,
                embedder_config=self.embedder_config,
                persist_path=persist_path,
            )
        else:
            raise ValueError(f"Unsupported RAG vector store type: {store_type}")

        if not self.vector_store:
            raise Exception("Failed to initialize RAG vector store.")


    def save(self, value: Any, metadata: Dict[str, Any]) -> None:
        if not self.vector_store:
            self._initialize_vector_store()
            if not self.vector_store: # Check again after attempt
                logger.error(f"RAG vector store not initialized for collection {self.collection_name}. Cannot save.")
                raise Exception(f"RAG vector store not initialized for collection {self.collection_name}")
        try:
            # RAGStorage previously used _generate_embedding, which added one doc at a time
            self.vector_store.add(
                documents=[str(value)], # Ensure value is string
                metadatas=[metadata or {}],
                ids=[str(uuid.uuid4())], # RAGStorage uses UUIDs for IDs
            )
        except Exception as e:
            logger.error(f"Error during RAG storage save for collection {self.collection_name}: {str(e)}")
            # Depending on desired behavior, may re-raise or handle

    def search(
        self,
        query: str,
        limit: int = 3,
        filter_criteria: Optional[dict] = None, # Renamed from filter
        score_threshold: float = 0.35,
        **kwargs
    ) -> List[Dict[str, Any]]: # Return type changed to List[Dict] to match old behavior
        if not self.vector_store:
            self._initialize_vector_store()
            if not self.vector_store:
                 logger.error(f"RAG vector store not initialized for collection {self.collection_name}. Cannot search.")
                 return []

        try:
            # VectorStoreInterface.search expects a list of query_texts
            search_results_lists = self.vector_store.search(
                query_texts=[query],
                n_results=limit,
                filter_criteria=filter_criteria,
                **kwargs
            )

            results = []
            if search_results_lists and search_results_lists[0]: # We passed one query, so take first list of results
                for res_item in search_results_lists[0]:
                    # Ensure score is not None before comparison
                    current_score = res_item.score if res_item.score is not None else -float('inf')
                    if current_score >= score_threshold:
                        results.append({
                            "id": res_item.id,
                            "context": res_item.document, # Map 'document' to 'context'
                            "metadata": res_item.metadata,
                            "score": res_item.score, # Score from VectorStoreQueryResult
                        })
            return results
        except Exception as e:
            logger.error(f"Error during RAG storage search for collection {self.collection_name}: {str(e)}")
            return []

    def reset(self) -> None:
        if self.vector_store:
            logger.info(f"Resetting RAGStorage collection '{self.collection_name}' via vector store.")
            self.vector_store.reset()
        else:
            logger.warning(f"RAG vector store not initialized for collection {self.collection_name}, nothing to reset.")

    # Removed _sanitize_role, _build_storage_file_name, _set_embedder_config,
    # _create_default_embedding_function, and _generate_embedding (logic moved to save)
    # as these are now handled by the vector store configuration or are obsolete.
    # The suppress_logging context manager is also removed as it was ChromaDB specific.
    # Logging within vector store implementations should be handled there.
