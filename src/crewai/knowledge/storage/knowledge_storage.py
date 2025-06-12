import hashlib
import logging
from typing import Any, Dict, List, Optional, Union

from crewai.knowledge.storage.base_knowledge_storage import BaseKnowledgeStorage
from crewai.utilities.logger import Logger
# Vector Store Interface and implementations
from crewai.vectorstores.base import (VectorStoreInterface,
                                     VectorStoreQueryResult)
# This line will be replaced by the alias in the next step,
# but for restoration, it should point to the original non-existent path
# or be a placeholder that the next step definitively replaces.
# For now, let's ensure it's the original problematic import, which will be fixed by aliasing.
from crewai.vectorstores.sqlite_store import SQLiteVectorStore as ChromaDBVectorStore

logger = logging.getLogger(__name__)

class KnowledgeStorage(BaseKnowledgeStorage):
    """
    Handles storage and retrieval of knowledge embeddings, using a configurable
    vector store backend.
    """

    vector_store: Optional[VectorStoreInterface] = None

    def __init__(
        self,
        storage_config: Dict[str, Any],
        embedder_config: Optional[Dict[str, Any]] = None,
    ):
        self.storage_config = storage_config
        self.embedder_config = embedder_config
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initializes the vector store based on the provided configuration."""
        store_type = self.storage_config.get("type", "chromadb").lower() # Default to chromadb
        collection_name = self.storage_config.get("collection_name", "crewai_knowledge")
        persist_path = self.storage_config.get("persist_path")

        logger.info(
            f"Initializing vector store: type='{store_type}', collection='{collection_name}', persist_path='{persist_path}'"
        )

        if store_type == "sqlite":
            self.vector_store = SQLiteVectorStore( # This will be the actual SQLiteVectorStore
                collection_name=collection_name,
                embedder_config=self.embedder_config,
                persist_path=persist_path,
            )
        elif store_type == "chromadb": # This will use the aliased SQLiteVectorStore
            self.vector_store = ChromaDBVectorStore(
                collection_name=collection_name,
                embedder_config=self.embedder_config,
                persist_path=persist_path,
            )
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")

        if not self.vector_store:
             raise Exception("Failed to initialize vector store.")


    def search(
        self,
        query: List[str],
        limit: int = 3,
        filter_criteria: Optional[dict] = None,
        score_threshold: float = 0.35,
        **kwargs
    ) -> List[Dict[str, Any]]:
        if not self.vector_store:
            self._initialize_vector_store()
            if not self.vector_store:
                 raise Exception("Vector store not initialized after attempt.")

        search_results_lists = self.vector_store.search(
            query_texts=query,
            n_results=limit,
            filter_criteria=filter_criteria,
            **kwargs
        )

        results = []
        if search_results_lists:
            for result_list_for_one_query in search_results_lists:
                for res_item in result_list_for_one_query:
                    current_score = res_item.score if res_item.score is not None else -float('inf')
                    if current_score >= score_threshold:
                        results.append({
                            "id": res_item.id,
                            "context": res_item.document,
                            "metadata": res_item.metadata,
                            "score": res_item.score,
                        })
        return results


    def reset(self):
        if self.vector_store:
            logger.info(f"Resetting KnowledgeStorage collection via vector store.")
            self.vector_store.reset()
        else:
            logger.warning("Vector store not initialized, nothing to reset.")


    def save(
        self,
        documents: List[str],
        metadata: Optional[Union[Dict[str, Any], List[Optional[Dict[str, Any]]]]] = None,
    ):
        if not self.vector_store:
            self._initialize_vector_store()
            if not self.vector_store:
                raise Exception("Vector store not initialized.")

        try:
            unique_docs_map: Dict[str, Tuple[str, Optional[Dict[str, Any]]]] = {}
            for idx, doc in enumerate(documents):
                doc_id = hashlib.sha256(doc.encode("utf-8")).hexdigest()
                doc_metadata: Optional[Dict[str, Any]] = None
                if metadata:
                    if isinstance(metadata, list):
                        doc_metadata = metadata[idx] if idx < len(metadata) else None
                    else:
                        doc_metadata = metadata
                unique_docs_map[doc_id] = (doc, doc_metadata)

            if not unique_docs_map:
                return

            final_ids = list(unique_docs_map.keys())
            final_docs = [unique_docs_map[doc_id][0] for doc_id in final_ids]
            final_metadatas = [unique_docs_map[doc_id][1] for doc_id in final_ids]

            self.vector_store.add(
                documents=final_docs,
                metadatas=final_metadatas, # type: ignore
                ids=final_ids,
            )
        except Exception as e:
            logger.error(f"Failed to save documents to vector store: {type(e).__name__} - {e}")
            if "dimension mismatch" in str(e).lower():
                 Logger(verbose=True).log(
                    "error",
                    "Embedding dimension mismatch. This usually happens when mixing different embedding models. Try resetting the collection.",
                    "red",
                )
                 raise ValueError(
                    "Embedding dimension mismatch. Make sure you're using the same embedding model "
                    "across all operations with this collection. Try resetting the collection."
                ) from e
            raise Exception(f"Failed to save documents: {e}") from e
