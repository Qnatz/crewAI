import contextlib
import hashlib
import io
import logging
import os
import shutil
from typing import Any, Dict, List, Optional, Union

# import chromadb # TODO: Remove chromadb
# import chromadb.errors # TODO: Remove chromadb
# from chromadb.api import ClientAPI # TODO: Remove chromadb
# from chromadb.api.types import OneOrMany # TODO: Remove chromadb
# from chromadb.config import Settings # TODO: Remove chromadb

from crewai.knowledge.storage.base_knowledge_storage import BaseKnowledgeStorage
from crewai.utilities import EmbeddingConfigurator
# from crewai.utilities.chromadb import sanitize_collection_name # TODO: Remove chromadb
from crewai.utilities.constants import KNOWLEDGE_DIRECTORY
from crewai.utilities.logger import Logger
from crewai.utilities.paths import db_storage_path


@contextlib.contextmanager
def suppress_logging(
    logger_name="chromadb.segment.impl.vector.local_persistent_hnsw", # TODO: Update logger_name
    level=logging.ERROR,
):
    logger = logging.getLogger(logger_name)
    original_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    with (
        contextlib.redirect_stdout(io.StringIO()),
        contextlib.redirect_stderr(io.StringIO()),
        contextlib.suppress(UserWarning),
    ):
        yield
    logger.setLevel(original_level)


class KnowledgeStorage(BaseKnowledgeStorage):
    """
    Extends Storage to handle embeddings for memory entries, improving
    search efficiency.
    """

    collection: Optional[Any] = None # TODO: Replace chromadb.Collection with a suitable type
    collection_name: Optional[str] = "knowledge"
    app: Optional[Any] = None # TODO: Replace ClientAPI with a suitable type

    def __init__(
        self,
        embedder: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
    ):
        self.collection_name = collection_name
        self._set_embedder_config(embedder)
        raise NotImplementedError("ChromaDB knowledge storage is no longer supported.")

    def search(
        self,
        query: List[str],
        limit: int = 3,
        filter: Optional[dict] = None,
        score_threshold: float = 0.35,
    ) -> List[Dict[str, Any]]:
        with suppress_logging():
            if self.collection:
                fetched = self.collection.query(
                    query_texts=query,
                    n_results=limit,
                    where=filter,
                )
                results = []
                for i in range(len(fetched["ids"][0])):  # type: ignore
                    result = {
                        "id": fetched["ids"][0][i],  # type: ignore
                        "metadata": fetched["metadatas"][0][i],  # type: ignore
                        "context": fetched["documents"][0][i],  # type: ignore
                        "score": fetched["distances"][0][i],  # type: ignore
                    }
                    if result["score"] >= score_threshold:
                        results.append(result)
                return results
            else:
                raise Exception("Collection not initialized")

    def initialize_knowledge_storage(self):
        # base_path = os.path.join(db_storage_path(), "knowledge") # TODO: Remove chromadb
        # chroma_client = chromadb.PersistentClient( # TODO: Remove chromadb
        #     path=base_path,
        #     settings=Settings(allow_reset=True),
        # )

        # self.app = chroma_client # TODO: Remove chromadb

        # try: # TODO: Remove chromadb
        #     collection_name = (
        #         f"knowledge_{self.collection_name}"
        #         if self.collection_name
        #         else "knowledge"
        #     )
        #     if self.app: # TODO: Remove chromadb
        #         self.collection = self.app.get_or_create_collection(
        #             name=sanitize_collection_name(collection_name), # TODO: Remove chromadb
        #             embedding_function=self.embedder,
        #         )
        #     else: # TODO: Remove chromadb
        #         raise Exception("Vector Database Client not initialized")
        # except Exception: # TODO: Remove chromadb
        #     raise Exception("Failed to create or get collection")
        raise NotImplementedError("ChromaDB knowledge storage is no longer supported.")

    def reset(self):
        # base_path = os.path.join(db_storage_path(), KNOWLEDGE_DIRECTORY) # TODO: Remove chromadb
        # if not self.app: # TODO: Remove chromadb
        #     self.app = chromadb.PersistentClient(
        #         path=base_path,
        #         settings=Settings(allow_reset=True),
        #     )

        # self.app.reset() # TODO: Remove chromadb
        # shutil.rmtree(base_path) # TODO: Remove chromadb
        # self.app = None # TODO: Remove chromadb
        # self.collection = None # TODO: Remove chromadb
        raise NotImplementedError("ChromaDB knowledge storage is no longer supported.")

    def save(
        self,
        documents: List[str],
        metadata: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        if not self.collection:
            raise Exception("Collection not initialized")

        try:
            # Create a dictionary to store unique documents
            unique_docs = {}

            # Generate IDs and create a mapping of id -> (document, metadata)
            for idx, doc in enumerate(documents):
                doc_id = hashlib.sha256(doc.encode("utf-8")).hexdigest()
                doc_metadata = None
                if metadata is not None:
                    if isinstance(metadata, list):
                        doc_metadata = metadata[idx]
                    else:
                        doc_metadata = metadata
                unique_docs[doc_id] = (doc, doc_metadata)

            # Prepare filtered lists for ChromaDB
            filtered_docs = []
            filtered_metadata = []
            filtered_ids = []

            # Build the filtered lists
            for doc_id, (doc, meta) in unique_docs.items():
                filtered_docs.append(doc)
                filtered_metadata.append(meta)
                filtered_ids.append(doc_id)

            # If we have no metadata at all, set it to None # TODO: Remove chromadb
            # final_metadata: Optional[OneOrMany[chromadb.Metadata]] = ( # TODO: Remove chromadb
            #     None if all(m is None for m in filtered_metadata) else filtered_metadata
            # )

            # self.collection.upsert( # TODO: Remove chromadb
            #     documents=filtered_docs,
            #     metadatas=final_metadata,
            #     ids=filtered_ids,
            # )
        # except chromadb.errors.InvalidDimensionException as e: # TODO: Remove chromadb
            # Logger(verbose=True).log(
                # "error",
                # "Embedding dimension mismatch. This usually happens when mixing different embedding models. Try resetting the collection using `crewai reset-memories -a`",
            #     "red",
            # )
            # raise ValueError(
            #     "Embedding dimension mismatch. Make sure you're using the same embedding model "
            #     "across all operations with this collection."
            #     "Try resetting the collection using `crewai reset-memories -a`"
            # ) from e
        except Exception as e: # TODO: Remove this try-except block if chromadb.errors.InvalidDimensionException is removed
            Logger(verbose=True).log("error", f"Failed to upsert documents: {e}", "red")
            raise
        raise NotImplementedError("ChromaDB knowledge storage is no longer supported.")

    def _create_default_embedding_function(self):
        # from chromadb.utils.embedding_functions.openai_embedding_function import ( # TODO: Remove chromadb
        #     OpenAIEmbeddingFunction,
        # )

        # return OpenAIEmbeddingFunction( # TODO: Remove chromadb
        #     api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
        # )
        raise NotImplementedError("ChromaDB knowledge storage is no longer supported.")

    def _set_embedder_config(self, embedder: Optional[Dict[str, Any]] = None) -> None:
        """Set the embedding configuration for the knowledge storage.

        Args:
            embedder_config (Optional[Dict[str, Any]]): Configuration dictionary for the embedder.
                If None or empty, defaults to the default embedding function.
        """
        self.embedder = (
            EmbeddingConfigurator().configure_embedder(embedder)
            if embedder
            else self._create_default_embedding_function()
        )
