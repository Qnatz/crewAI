import hashlib
import json
import logging
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from crewai.utilities import EmbeddingConfigurator
from crewai.vectorstores.base import (VectorStoreInterface,
                                     VectorStoreQueryResult)

logger = logging.getLogger(__name__)

class EnhancedSQLiteDB:
    """
    A SQLite database class for storing and retrieving text embeddings
    with metadata and supporting metadata-based filtering.
    """

    def __init__(self, db_path: Path, table_name: str = "vector_store"):
        self.db_path = db_path
        self.table_name = table_name.replace('-', '_') # Ensure table name is SQL friendly
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._connect()
        self._create_table_if_not_exists()

    def _connect(self):
        try:
            self._conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            self._cursor = self._conn.cursor()
            logger.debug(f"Connected to SQLite DB at {self.db_path} for table {self.table_name}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to SQLite database {self.db_path}: {e}")
            raise

    def _create_table_if_not_exists(self):
        if not self._cursor:
            self._connect() # Should not happen if constructor called _connect

        try:
            self._cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    item_id TEXT PRIMARY KEY,
                    content TEXT,
                    embedding BLOB,
                    metadata_json TEXT
                )
                """
            )
            self._conn.commit()
            logger.debug(f"Table {self.table_name} ensured to exist.")
        except sqlite3.Error as e:
            logger.error(f"Error creating table {self.table_name}: {e}")
            raise

    def store_embeddings(
        self,
        item_ids: List[str],
        contents: List[str],
        embeddings: List[np.ndarray],
        metadatas: Optional[List[Optional[Dict[str, Any]]]] = None,
    ):
        if not (len(item_ids) == len(contents) == len(embeddings)):
            raise ValueError("item_ids, contents, and embeddings must have the same length.")
        if metadatas and len(metadatas) != len(item_ids):
            raise ValueError("metadatas list, if provided, must have the same length as item_ids.")

        if not self._conn or not self._cursor: self._connect()

        try:
            for i, item_id in enumerate(item_ids):
                content = contents[i]
                embedding_blob = embeddings[i].tobytes()
                metadata_str = json.dumps(metadatas[i]) if metadatas and metadatas[i] else "{}"

                self._cursor.execute(
                    f"""
                    INSERT OR REPLACE INTO {self.table_name} (item_id, content, embedding, metadata_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (item_id, content, embedding_blob, metadata_str),
                )
            self._conn.commit()
            logger.debug(f"Stored/Replaced {len(item_ids)} embeddings in table {self.table_name}.")
        except sqlite3.Error as e:
            logger.error(f"Error storing embeddings in table {self.table_name}: {e}")
            self._conn.rollback()
            raise

    def retrieve_similar_items(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self._conn or not self._cursor: self._connect()

        base_query = f"SELECT item_id, content, embedding, metadata_json FROM {self.table_name}"
        conditions = []
        params = []

        if filter_criteria:
            for key, value in filter_criteria.items():
                # Assuming simple equality for filtering. Adjust if more complex queries are needed.
                # For nested JSON, use json_extract(metadata_json, '$.path.to.key')
                # This example assumes top-level keys in metadata for simplicity of filter_criteria.
                # A more robust solution would parse filter_criteria to build complex JSON path queries.
                if isinstance(value, (str, int, float, bool)):
                    conditions.append(f"json_extract(metadata_json, '$.{key}') = ?")
                    params.append(value)
                else:
                    logger.warning(f"Unsupported filter value type for key '{key}': {type(value)}. Skipping this filter.")

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        try:
            self._cursor.execute(base_query, tuple(params))
            rows = self._cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error retrieving items from table {self.table_name}: {e}")
            return []

        if not rows:
            return []

        results = []
        for row in rows:
            item_id, content, embedding_blob, metadata_json = row
            embedding = np.frombuffer(embedding_blob, dtype=np.float32) # Assuming float32, adjust if necessary

            # Cosine similarity: (A . B) / (||A|| * ||B||)
            # NumPy's dot product for A.B
            # np.linalg.norm for ||A|| and ||B||
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )

            results.append({
                "id": item_id,
                "document": content,
                "metadata": json.loads(metadata_json or "{}"),
                "score": float(similarity) # Higher is better for cosine similarity
            })

        # Sort by similarity score in descending order and take top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def clear_table(self):
        if not self._conn or not self._cursor: self._connect()
        try:
            self._cursor.execute(f"DELETE FROM {self.table_name}")
            self._conn.commit()
            logger.info(f"Table {self.table_name} cleared.")
        except sqlite3.Error as e:
            logger.error(f"Error clearing table {self.table_name}: {e}")
            self._conn.rollback()
            raise

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None
            logger.debug(f"Closed connection to SQLite DB {self.db_path}")


class SQLiteVectorStore(VectorStoreInterface):
    def __init__(self,
                 collection_name: str,
                 embedder_config: Optional[Dict[str, Any]] = None,
                 persist_path: Optional[str] = None,
                 **kwargs):
        super().__init__(collection_name, embedder_config, persist_path, **kwargs)

        if persist_path is None:
            # Default to a standard crewAI directory if no path is given.
            # Using a hidden directory in user's home for broader compatibility.
            persist_path = str(Path.home() / ".crewai" / "vectorstores")
            logger.info(f"No persist_path provided, defaulting to: {persist_path}")

        self.persist_path = Path(persist_path)
        self.collection_name = collection_name.replace("-", "_") # SQL friendly

        db_file_name = f"{self.collection_name}.db"
        self.db_path = self.persist_path / db_file_name

        self.db = EnhancedSQLiteDB(db_path=self.db_path, table_name=self.collection_name)

        self.embedder = EmbeddingConfigurator().configure_embedder(config=embedder_config or {})
        if not callable(self.embedder):
             # Chroma EmbeddingFunctions are callable. If configure_embedder returns something else,
             # we might need to access a specific method.
             # For now, assuming it's directly callable or has a __call__ method.
            logger.warning("Configured embedder might not be directly callable. Assuming it has a __call__ method for List[str].")


    def add(self,
            documents: List[str],
            metadatas: Optional[List[Optional[Dict[str, Any]]]] = None,
            ids: Optional[List[str]] = None) -> None:

        if not documents:
            logger.debug("No documents provided to add.")
            return

        doc_ids = ids if ids else []
        if not ids:
            for doc in documents:
                doc_ids.append(hashlib.md5(doc.encode()).hexdigest())

        # Ensure metadatas list matches documents list structure if not provided properly
        if metadatas is None:
            metadatas = [{} for _ in documents]
        elif len(metadatas) != len(documents):
            logger.warning("Length of metadatas does not match documents. Using empty metadata for missing ones.")
            # Pad metadatas or use default if lengths don't match
            # This ensures each document has corresponding metadata, even if it's just {}
            processed_metadatas = []
            for i in range(len(documents)):
                processed_metadatas.append(metadatas[i] if i < len(metadatas) and metadatas[i] is not None else {})
            metadatas = processed_metadatas


        try:
            # Assuming self.embedder can take a list of documents and return a list of embeddings
            embeddings_list_of_lists = self.embedder(documents) # type: ignore

            # Convert to list of np.ndarray
            np_embeddings: List[np.ndarray] = []
            for emb in embeddings_list_of_lists:
                np_embeddings.append(np.array(emb, dtype=np.float32))

        except Exception as e:
            error_message = f"Embedding generation failed in SQLiteVectorStore for collection '{self.collection_name}' during 'add' operation. This may be due to an issue with the embedding model configuration, network connectivity, API keys, or missing underlying dependencies (e.g., 'onnxruntime' for specific models). Original error: {type(e).__name__}: {e}"
            logger.error(error_message)
            raise RuntimeError(error_message) from e

        if not np_embeddings or len(np_embeddings) != len(documents):
            logger.error("Embedding generation failed or returned unexpected number of embeddings.")
            return

        self.db.store_embeddings(
            item_ids=doc_ids,
            contents=documents,
            embeddings=np_embeddings,
            metadatas=metadatas
        )

    def search(self,
               query_texts: List[str],
               n_results: int = 5,
               filter_criteria: Optional[Dict[str, Any]] = None) -> List[List[VectorStoreQueryResult]]:

        all_results: List[List[VectorStoreQueryResult]] = []
        if not query_texts:
            return all_results

        for query_text in query_texts:
            try:
                # Assuming embedder can also embed a single query text.
                query_embedding_list = self.embedder([query_text]) # type: ignore
                if not query_embedding_list or not query_embedding_list[0]:
                    logger.error(f"Failed to embed query text (empty result from embedder): {query_text} in collection {self.collection_name}")
                    all_results.append([])
                    continue

                query_embedding_np = np.array(query_embedding_list[0], dtype=np.float32)

            except Exception as e:
                error_message = f"Embedding generation failed in SQLiteVectorStore for query '{query_text}' in collection '{self.collection_name}' during 'search' operation. This may be due to an issue with the embedding model configuration, network connectivity, API keys, or missing underlying dependencies (e.g., 'onnxruntime' for specific models). Original error: {type(e).__name__}: {e}"
                logger.error(error_message)
                # Decide if one failed query embedding should stop all, or just skip this query
                all_results.append([]) # Add empty result for this query
                continue # Continue to next query text

            db_search_results = self.db.retrieve_similar_items(
                query_embedding=query_embedding_np,
                top_k=n_results,
                filter_criteria=filter_criteria
            )

            current_query_results = []
            for res in db_search_results:
                current_query_results.append(
                    VectorStoreQueryResult(
                        id=res["id"],
                        document=res["document"],
                        metadata=res["metadata"],
                        score=res["score"]
                    )
                )
            all_results.append(current_query_results)

        return all_results

    def reset(self) -> None:
        """Clears all entries in the specific collection's table."""
        logger.info(f"Resetting vector store for collection: {self.collection_name}")
        self.db.clear_table()

    def __del__(self):
        """Ensure database connection is closed when the object is deleted."""
        if hasattr(self, 'db') and self.db:
            self.db.close()

# Example usage (for testing purposes, not part of the library code)
if __name__ == '__main__':
    # This example assumes you have an embedder_config that works with EmbeddingConfigurator
    # For instance, for OpenAI:
    # embedder_cfg = {"provider": "openai", "config": {"model": "text-embedding-ada-002", "api_key": "YOUR_API_KEY"}}
    # Or for a local SentenceTransformer model via LiteLLM/SentenceTransformers
    # embedder_cfg = {"provider": "litellm", "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}}

    # A mock embedder for local testing without API keys / heavy models
    class MockEmbedder:
        def __call__(self, texts: List[str]) -> List[List[float]]:
            embeddings = []
            for i, text in enumerate(texts):
                # Simple hash-based embedding for consistent but unique-ish vectors
                h = hashlib.md5(text.encode()).digest()
                # Create a fixed-size embedding, e.g., 10 dimensions
                emb = [float(b + i) / 255.0 for b in h[:10]]
                embeddings.append(emb)
            return embeddings

    # Replace EmbeddingConfigurator for this test
    class MockEmbeddingConfigurator:
        def configure_embedder(self, config: Optional[Dict[str, Any]] = None):
            logger.info("Using MockEmbedder for testing.")
            return MockEmbedder()

    # Monkey patch the real configurator for this test script
    import crewai.vectorstores.sqlite_store as current_module
    current_module.EmbeddingConfigurator = MockEmbeddingConfigurator # type: ignore

    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting SQLiteVectorStore example usage...")

    # Define a persist_path for the database
    test_persist_path = Path("./test_vector_stores")
    test_persist_path.mkdir(parents=True, exist_ok=True)

    # Initialize the vector store
    collection_name = "test_collection"
    # No embedder_config needed for mock, but pass empty dict
    sqlite_vs = SQLiteVectorStore(collection_name=collection_name, persist_path=str(test_persist_path), embedder_config={})

    # Add some documents
    docs_to_add = [
        "CrewAI is a framework for orchestrating role-playing, autonomous AI agents.",
        "SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.",
        "Termux is an Android terminal emulator and Linux environment app that works directly with no rooting or setup required."
    ]
    metadata_to_add = [
        {"source": "crewai_docs", "type": "framework"},
        {"source": "sqlite_docs", "type": "database"},
        {"source": "termux_wiki", "type": "android_app"}
    ]
    ids_to_add = ["doc1", "doc2", "doc3"]

    logger.info(f"\n--- Adding documents to {collection_name} ---")
    sqlite_vs.add(documents=docs_to_add, metadatas=metadata_to_add, ids=ids_to_add)
    logger.info("Documents added.")

    # Search for similar documents
    logger.info("\n--- Searching for 'AI framework' ---")
    search_results_1 = sqlite_vs.search(query_texts=["AI framework"], n_results=2)
    for i, result_group in enumerate(search_results_1):
        logger.info(f"Results for query {i+1}:")
        for res_item in result_group:
            logger.info(f"  ID: {res_item.id}, Score: {res_item.score:.4f}, Doc: {res_item.document_preview(30) if hasattr(res_item, 'document_preview') else res_item.document[:30] + '...'}") # Added preview for brevity
            logger.info(f"     Metadata: {res_item.metadata}")


    logger.info("\n--- Searching for 'SQL database' with filter {'source': 'sqlite_docs'} ---")
    search_results_2 = sqlite_vs.search(query_texts=["SQL database"], n_results=2, filter_criteria={"source": "sqlite_docs"})
    for i, result_group in enumerate(search_results_2):
        logger.info(f"Results for query {i+1} (filtered):")
        for res_item in result_group:
            logger.info(f"  ID: {res_item.id}, Score: {res_item.score:.4f}, Doc: {res_item.document_preview(30) if hasattr(res_item, 'document_preview') else res_item.document[:30] + '...'}")
            logger.info(f"     Metadata: {res_item.metadata}")
            assert res_item.metadata.get("source") == "sqlite_docs"


    logger.info("\n--- Searching for 'terminal emulator' (should find Termux) ---")
    search_results_3 = sqlite_vs.search(query_texts=["terminal emulator"], n_results=1)
    for i, result_group in enumerate(search_results_3):
        logger.info(f"Results for query {i+1}:")
        for res_item in result_group:
            logger.info(f"  ID: {res_item.id}, Score: {res_item.score:.4f}, Doc: {res_item.document_preview(30) if hasattr(res_item, 'document_preview') else res_item.document[:30] + '...'}")
            logger.info(f"     Metadata: {res_item.metadata}")
            assert "Termux" in res_item.document

    # Test reset
    logger.info(f"\n--- Resetting collection {collection_name} ---")
    sqlite_vs.reset()
    logger.info("Collection reset.")

    logger.info("\n--- Searching after reset (should be empty) ---")
    search_results_after_reset = sqlite_vs.search(query_texts=["AI framework"], n_results=2)
    if not any(search_results_after_reset):
        logger.info("Search results are empty as expected after reset.")
    else:
        logger.error(f"Search results not empty after reset: {search_results_after_reset}")

    # Clean up the test database file
    try:
        sqlite_vs.db_path.unlink()
        logger.info(f"Test database file {sqlite_vs.db_path} deleted.")
    except OSError as e:
        logger.error(f"Error deleting test database file {sqlite_vs.db_path}: {e}")

    logger.info("\nExample usage finished.")

    # Add document_preview to VectorStoreQueryResult for cleaner logging in example
    def document_preview(self, length=50):
        if self.document:
            return (self.document[:length] + '...') if len(self.document) > length else self.document
        return None
    VectorStoreQueryResult.document_preview = document_preview # type: ignore
