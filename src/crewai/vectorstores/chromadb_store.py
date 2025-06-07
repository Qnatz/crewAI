import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.api.types import EmbeddingFunction

from crewai.utilities import EmbeddingConfigurator
from crewai.vectorstores.base import (VectorStoreInterface,
                                     VectorStoreQueryResult)

logger = logging.getLogger(__name__)

class ChromaDBVectorStore(VectorStoreInterface):
    """
    Implements the VectorStoreInterface for ChromaDB.
    """

    def __init__(self,
                 collection_name: str,
                 embedder_config: Optional[Dict[str, Any]] = None,
                 persist_path: Optional[str] = None,
                 **kwargs):
        super().__init__(collection_name, embedder_config, persist_path, **kwargs)

        if persist_path is None:
            persist_path = str(Path.home() / ".crewai" / "vectorstores" / "chroma_data")
            logger.info(f"No persist_path provided for ChromaDB, defaulting to: {persist_path}")

        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name # ChromaDB handles sanitization if needed or use sanitize_collection_name utility

        try:
            self.client = chromadb.PersistentClient(path=str(self.persist_path))
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB PersistentClient at {self.persist_path}: {e}")
            raise

        embedding_configurator = EmbeddingConfigurator(config=embedder_config or {})
        try:
            self.embedding_function: Optional[EmbeddingFunction] = embedding_configurator.configure_embedder()
        except Exception as e:
            error_message = f"Failed to configure embedder for ChromaDB collection '{self.collection_name}'. This may be due to an issue with the embedding model configuration or missing underlying dependencies (e.g., 'onnxruntime' for specific models). Original error: {type(e).__name__}: {e}"
            logger.error(error_message)
            raise RuntimeError(error_message) from e

        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function # type: ignore
            )
            collection_metadata = self.collection.metadata
            self._space = "l2" # default
            if collection_metadata and "hnsw:space" in collection_metadata:
                 self._space = collection_metadata["hnsw:space"]
            elif self.embedding_function and hasattr(self.embedding_function, 'cs_default_space'):
                 self._space = getattr(self.embedding_function, 'cs_default_space', 'l2')

            logger.info(f"ChromaDB collection '{self.collection_name}' loaded/created. Space: {self._space}")

        except Exception as e:
            error_message = f"Failed to get or create ChromaDB collection '{self.collection_name}'. This could be due to issues with ChromaDB setup, permissions, or an issue with the (potentially pre-configured) embedding function if it was validated at this stage. Original error: {type(e).__name__}: {e}"
            logger.error(error_message)
            raise RuntimeError(error_message) from e

    def _calculate_score(self, distance: float) -> float:
        """Converts distance to a similarity score (higher is better)."""
        if self._space == "cosine":
            return 1.0 - distance  # Cosine distance is 1 - similarity
        elif self._space == "l2":
            # L2 distance (Euclidean) is non-negative; smaller is better.
            # Invert and normalize: 1 / (1 + distance)
            return 1.0 / (1.0 + distance)
        else: # For "ip" (inner product), distance might already be score-like or need specific handling
              # Defaulting to just returning the distance if space is unknown, assuming it might be a score.
            logger.warning(f"Unknown or unhandled distance space '{self._space}'. Returning raw distance as score.")
            return distance


    def add(self,
            documents: List[str],
            metadatas: Optional[List[Optional[Dict[str, Any]]]] = None,
            ids: Optional[List[str]] = None) -> None:

        if not documents:
            logger.debug("No documents provided to add to ChromaDB.")
            return

        doc_ids = ids if ids else []
        if not ids:
            for doc_content in documents:
                doc_ids.append(hashlib.md5(doc_content.encode()).hexdigest())

        # Ensure metadatas list matches documents list structure
        processed_metadatas: List[Dict[str, Any]] = []
        if metadatas is None:
            processed_metadatas = [{} for _ in documents]
        else:
            if len(metadatas) != len(documents):
                logger.warning("Length of metadatas does not match documents. Padding with empty metadata.")
            for i in range(len(documents)):
                processed_metadatas.append(metadatas[i] if i < len(metadatas) and metadatas[i] is not None else {})

        try:
            self.collection.upsert(
                ids=doc_ids,
                documents=documents,
                metadatas=processed_metadatas
            )
            logger.debug(f"Upserted {len(documents)} documents into ChromaDB collection '{self.collection_name}'.")
        except chromadb.errors.ChromaError as ce:
            error_message = f"ChromaDB operation failed during 'add' in collection '{self.collection_name}'. This might be due to an embedding function error (e.g., misconfiguration, network, API keys, or missing dependencies like 'onnxruntime'). Original error: {type(ce).__name__}: {ce}"
            logger.error(error_message)
            raise RuntimeError(error_message) from ce
        except Exception as e:
            error_message = f"Unexpected error during 'add' in ChromaDB collection '{self.collection_name}'. Original error: {type(e).__name__}: {e}"
            logger.error(error_message)
            raise RuntimeError(error_message) from e


    def search(self,
               query_texts: List[str],
               n_results: int = 5,
               filter_criteria: Optional[Dict[str, Any]] = None) -> List[List[VectorStoreQueryResult]]:

        all_query_results: List[List[VectorStoreQueryResult]] = []
        if not query_texts:
            return all_query_results

        try:
            query_results_chroma = self.collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=filter_criteria
            )
        except chromadb.errors.ChromaError as ce:
            error_message = f"ChromaDB query operation failed for collection '{self.collection_name}'. This might be due to an embedding function error if query_texts were provided and needed embedding (e.g., misconfiguration, network, API keys, or missing dependencies like 'onnxruntime'). Original error: {type(ce).__name__}: {ce}"
            logger.error(error_message)
            return [[] for _ in query_texts] # Return empty results for all queries
        except Exception as e:
            error_message = f"Unexpected error during 'search' in ChromaDB collection '{self.collection_name}'. Original error: {type(e).__name__}: {e}"
            logger.error(error_message)
            return [[] for _ in query_texts]


        # ChromaDB query_results structure (example for 1 query_text):
        # {
        #   'ids': [['id1', 'id2']],
        #   'documents': [['doc1_content', 'doc2_content']],
        #   'metadatas': [[{'meta1': 'val1'}, {'meta2': 'val2'}]],
        #   'distances': [[0.1, 0.2]]
        # }
        # We need to parse this into List[List[VectorStoreQueryResult]]

        chroma_ids = query_results_chroma.get('ids', [])
        chroma_documents = query_results_chroma.get('documents', [])
        chroma_metadatas = query_results_chroma.get('metadatas', [])
        chroma_distances = query_results_chroma.get('distances', [])

        num_queries = len(query_texts)
        for i in range(num_queries):
            single_query_formatted_results: List[VectorStoreQueryResult] = []

            # Ensure all lists have data for query i
            current_ids = chroma_ids[i] if chroma_ids and i < len(chroma_ids) else []
            current_docs = chroma_documents[i] if chroma_documents and i < len(chroma_documents) else [None] * len(current_ids)
            current_metas = chroma_metadatas[i] if chroma_metadatas and i < len(chroma_metadatas) else [{}] * len(current_ids)
            current_dists = chroma_distances[i] if chroma_distances and i < len(chroma_distances) else [float('inf')] * len(current_ids)

            for j, doc_id in enumerate(current_ids):
                doc_content = current_docs[j] if j < len(current_docs) else None
                doc_meta = current_metas[j] if j < len(current_metas) else {}
                doc_dist = current_dists[j] if j < len(current_dists) else float('inf')

                score = self._calculate_score(doc_dist)

                single_query_formatted_results.append(
                    VectorStoreQueryResult(
                        id=doc_id,
                        document=doc_content,
                        metadata=doc_meta,
                        score=score
                    )
                )
            all_query_results.append(single_query_formatted_results)

        return all_query_results

    def reset(self) -> None:
        """
        Deletes and recreates the collection in ChromaDB.
        """
        logger.info(f"Resetting ChromaDB collection: {self.collection_name}")
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.debug(f"Deleted collection '{self.collection_name}'. Recreating...")
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function # type: ignore
            )
            logger.info(f"Collection '{self.collection_name}' reset and recreated.")
        except Exception as e:
            logger.error(f"Error resetting ChromaDB collection '{self.collection_name}': {e}. Trying to create it again.")
            try:
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function # type: ignore
                )
                logger.info(f"Collection '{self.collection_name}' created after reset attempt failed to delete first.")
            except Exception as e_create:
                logger.error(f"Failed to create collection '{self.collection_name}' even after reset error: {e_create}")
                raise


# Example usage (for testing purposes, not part of the library code)
if __name__ == '__main__':
    # This example assumes you have an embedder_config that works with EmbeddingConfigurator
    # For instance, for OpenAI:
    # embedder_cfg = {"provider": "openai", "config": {"model": "text-embedding-ada-002", "api_key": "YOUR_API_KEY"}}
    # Or for a local SentenceTransformer model via LiteLLM/SentenceTransformers
    # embedder_cfg = {"provider": "litellm", "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}}

    # A mock embedder for local testing without API keys / heavy models
    class MockChromaEmbedder(EmbeddingFunction):
        def __init__(self):
            # Determine dimensionality for mock embeddings
            sample_text_for_dim = "determine_dim"
            h_sample = hashlib.md5(sample_text_for_dim.encode()).digest()
            self.dim = len([float(b) / 255.0 for b in h_sample[:16]]) # e.g. 16 dimensions

        def __call__(self, texts: List[str]) -> List[List[float]]:
            embeddings = []
            for i, text in enumerate(texts):
                h = hashlib.md5(text.encode()).digest()
                emb = [float(b + i) / 255.0 for b in h[:self.dim]]
                embeddings.append(emb)
            return embeddings

        # Required by ChromaDB for some operations like creating collection if no explicit dim passed
        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            return self(texts)

        def embed_query(self, query: str) -> List[float]:
            return self([query])[0]


    class MockEmbeddingConfiguratorChroma:
        def configure_embedder(self, config: Optional[Dict[str, Any]] = None):
            logger.info("Using MockChromaEmbedder for testing ChromaDBVectorStore.")
            return MockChromaEmbedder() # type: ignore

    # Monkey patch the real configurator for this test script
    import crewai.vectorstores.chromadb_store as current_module
    current_module.EmbeddingConfigurator = MockEmbeddingConfiguratorChroma # type: ignore

    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting ChromaDBVectorStore example usage...")

    test_persist_path_chroma = Path("./test_chroma_vector_stores")

    # Clean up previous test run if any
    import shutil
    if test_persist_path_chroma.exists():
        shutil.rmtree(test_persist_path_chroma)
        logger.info(f"Cleaned up old data at {test_persist_path_chroma}")
    test_persist_path_chroma.mkdir(parents=True, exist_ok=True)


    collection_name_chroma = "test_chroma_collection"
    chroma_vs = ChromaDBVectorStore(collection_name=collection_name_chroma,
                                    persist_path=str(test_persist_path_chroma),
                                    embedder_config={}) # Mocked, config content doesn't matter here

    docs_to_add_chroma = [
        "ChromaDB is a great vector database for AI applications.",
        "It supports various embedding functions and distance metrics.",
        "CrewAI can leverage ChromaDB for RAG capabilities."
    ]
    metadata_to_add_chroma = [
        {"source": "chroma_website", "version": "latest"},
        {"source": "chroma_docs", "version": "0.4.x"},
        {"source": "crewai_docs", "feature": "RAG"}
    ]
    ids_to_add_chroma = ["chroma_doc1", "chroma_doc2", "crewai_chroma_doc"]

    logger.info(f"\n--- Adding documents to {collection_name_chroma} ---")
    chroma_vs.add(documents=docs_to_add_chroma, metadatas=metadata_to_add_chroma, ids=ids_to_add_chroma)
    logger.info("Documents added to ChromaDB.")

    logger.info("\n--- Searching for 'vector database' ---")
    search_results_chroma_1 = chroma_vs.search(query_texts=["vector database"], n_results=2)
    for i, result_group in enumerate(search_results_chroma_1):
        logger.info(f"Results for query {i+1}:")
        for res_item in result_group:
            doc_preview = (res_item.document[:30] + '...') if res_item.document and len(res_item.document) > 30 else res_item.document
            logger.info(f"  ID: {res_item.id}, Score: {res_item.score:.4f}, Doc: {doc_preview}")
            logger.info(f"     Metadata: {res_item.metadata}")

    logger.info("\n--- Searching for 'RAG' with filter {'source': 'crewai_docs'} ---")
    search_results_chroma_2 = chroma_vs.search(query_texts=["RAG"], n_results=1, filter_criteria={"source": "crewai_docs"})
    for i, result_group in enumerate(search_results_chroma_2):
        logger.info(f"Results for query {i+1} (filtered):")
        for res_item in result_group:
            doc_preview = (res_item.document[:30] + '...') if res_item.document and len(res_item.document) > 30 else res_item.document
            logger.info(f"  ID: {res_item.id}, Score: {res_item.score:.4f}, Doc: {doc_preview}")
            logger.info(f"     Metadata: {res_item.metadata}")
            assert res_item.metadata.get("source") == "crewai_docs"

    logger.info(f"\n--- Resetting collection {collection_name_chroma} ---")
    chroma_vs.reset()
    logger.info("ChromaDB collection reset.")

    logger.info("\n--- Searching after reset (should be empty) ---")
    search_results_after_reset_chroma = chroma_vs.search(query_texts=["vector database"], n_results=2)
    if not any(search_results_after_reset_chroma) or not search_results_after_reset_chroma[0]:
        logger.info("Search results are empty as expected after reset.")
    else:
        logger.error(f"Search results not empty after reset: {search_results_after_reset_chroma}")

    # Clean up the test database directory
    try:
        shutil.rmtree(test_persist_path_chroma)
        logger.info(f"Test ChromaDB directory {test_persist_path_chroma} deleted.")
    except OSError as e:
        logger.error(f"Error deleting test ChromaDB directory {test_persist_path_chroma}: {e}")

    logger.info("\nChromaDBVectorStore example usage finished.")
