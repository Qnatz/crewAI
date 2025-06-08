import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import lancedb
import pyarrow as pa
import numpy as np

from crewai.vectorstores.base import (
    VectorStoreInterface,
    VectorStoreQueryResult,
)
from crewai.utilities import EmbeddingConfigurator
from crewai.utilities.paths import db_storage_path

logger = logging.getLogger(__name__)

class LanceDBVectorStore(VectorStoreInterface):
    def __init__(
        self,
        collection_name: str,
        embedder_config: Optional[Dict[str, Any]] = None,
        persist_path: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(collection_name, embedder_config, persist_path, **kwargs)

        self.collection_name = collection_name.replace("-", "_")
        if persist_path is None:
            base_persist_path = db_storage_path() / "lancedb_stores"
            logger.info(f"No persist_path provided, defaulting base to: {base_persist_path}")
        else:
            base_persist_path = Path(persist_path)

        self.db_uri = str(base_persist_path / self.collection_name)
        Path(self.db_uri).parent.mkdir(parents=True, exist_ok=True)

        try:
            self.db = lancedb.connect(self.db_uri)
            logger.info(f"Connected to LanceDB at URI '{self.db_uri}'.")
        except Exception as e:
            logger.error(f"Failed to connect to LanceDB at URI '{self.db_uri}': {e}")
            raise RuntimeError(f"Failed to connect to LanceDB: {e}") from e

        try:
            self.embedder = EmbeddingConfigurator().configure_embedder(
                config=embedder_config or {}
            )
            if not callable(self.embedder) and not hasattr(self.embedder, 'embed_documents'):
                 logger.warning("Configured embedder might not be directly callable or have an 'embed_documents' method. Assuming it has a __call__ method for List[str].")
        except Exception as e:
            logger.error(f"Failed to configure embedder for LanceDBVectorStore: {e}")
            raise RuntimeError(f"Failed to configure embedder: {e}") from e

        self._embedding_dimension: Optional[int] = None
        self.schema: Optional[pa.Schema] = None # Initialize schema attribute

        try:
            if hasattr(self.embedder, 'get_embedding_dimension'):
                self._embedding_dimension = self.embedder.get_embedding_dimension()
            elif hasattr(self.embedder, '_client') and hasattr(self.embedder._client, 'get_sentence_embedding_dimension'): # common for sentence-transformers
                self._embedding_dimension = self.embedder._client.get_sentence_embedding_dimension()
            elif hasattr(self.embedder, 'dim'): # some models store it as 'dim'
                 self._embedding_dimension = self.embedder.dim
            elif hasattr(self.embedder, 'dimension'):
                 self._embedding_dimension = self.embedder.dimension
            else:
                if not callable(self.embedder):
                    raise TypeError("Embedder is not callable, cannot determine dimension.")
                dummy_embedding_list = self.embedder(["test"])
                if not isinstance(dummy_embedding_list, list) or not dummy_embedding_list:
                    raise ValueError("Embedder did not return a valid list of embeddings.")
                dummy_embedding = dummy_embedding_list[0]
                if not hasattr(dummy_embedding, '__len__'):
                     raise ValueError("Embedding result does not have a determinable length.")
                self._embedding_dimension = len(dummy_embedding)
            logger.info(f"Determined embedding dimension: {self._embedding_dimension}")
        except Exception as e:
            logger.warning(f"Could not reliably determine embedding dimension during init: {e}. Will attempt schema inference if table is created.")

        if self._embedding_dimension:
            self.schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("document", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), list_size=self._embedding_dimension)),
                pa.field("metadata", pa.string())
            ])
        else:
            # Fallback schema if dimension couldn't be determined.
            self.schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("document", pa.string()),
                pa.field("embedding", pa.list_(pa.float32())), # No list_size
                pa.field("metadata", pa.string())
            ])
            logger.info("Using schema without fixed vector size due to undetermined embedding dimension at init.")


        try:
            if self.collection_name in self.db.table_names():
                self.table = self.db.open_table(self.collection_name)
                logger.info(f"Opened existing LanceDB table '{self.collection_name}'.")
                # Optional: verify schema compatibility if possible
                # For example, check if 'embedding' field list_size matches self._embedding_dimension if known
                if self.table.schema and self._embedding_dimension:
                    table_emb_field = self.table.schema.field("embedding")
                    if hasattr(table_emb_field.type, 'list_size') and table_emb_field.type.list_size != self._embedding_dimension:
                        logger.warning(f"Opened table schema's embedding dimension ({table_emb_field.type.list_size}) "
                                       f"differs from determined dimension ({self._embedding_dimension}). This might lead to issues.")
            else:
                logger.info(f"LanceDB table '{self.collection_name}' not found. Will be created on first add or explicitly if schema is fully known.")
                if self._embedding_dimension and self.schema: # If dimension is known, create table now
                    self.table = self.db.create_table(self.collection_name, schema=self.schema)
                    logger.info(f"Created LanceDB table '{self.collection_name}' with explicit schema (dim={self._embedding_dimension}).")
                else:
                    self.table = None # Mark table as not yet created
                    logger.info(f"Table '{self.collection_name}' will be created on first data addition to infer schema, as embedding dimension is not yet known.")

        except Exception as e:
            logger.error(f"Error during __init__ table handling for '{self.collection_name}': {e}")
            self.table = None # Ensure table is None if setup failed


    def _ensure_table_exists_with_data_for_schema_inference(self, sample_doc_for_embedding: str = "schema_inference_dummy_doc"):
        """Internal method to create table by inferring schema from dummy data if not already created."""
        if self.table:
            return

        logger.info(f"Ensuring table '{self.collection_name}' exists...")
        if self.collection_name in self.db.table_names():
            self.table = self.db.open_table(self.collection_name)
            logger.info(f"Table '{self.collection_name}' opened.")
            return

        if not self._embedding_dimension: # Dimension is unknown, try to infer
            logger.info("Attempting to determine embedding dimension and create table by inferring schema.")
            try:
                if not callable(self.embedder):
                    raise TypeError("Embedder is not callable, cannot infer schema.")
                dummy_emb_list = self.embedder([sample_doc_for_embedding])
                if not dummy_emb_list or not isinstance(dummy_emb_list, list) or not dummy_emb_list[0]:
                    raise ValueError("Dummy embedding for schema inference failed or returned empty.")

                raw_dummy_emb = dummy_emb_list[0]
                dummy_vector_for_schema: List[float]
                if hasattr(raw_dummy_emb, 'tolist'):
                    dummy_vector_for_schema = raw_dummy_emb.tolist()
                elif isinstance(raw_dummy_emb, list) and all(isinstance(e_val, (float, int, np.float32, np.float64)) for e_val in raw_dummy_emb):
                    dummy_vector_for_schema = [float(e_val) for e_val in raw_dummy_emb]
                else:
                    raise ValueError("Dummy embedding could not be converted to list of floats for schema inference.")

                self._embedding_dimension = len(dummy_vector_for_schema)

                # Update self.schema with the now known dimension
                self.schema = pa.schema([
                    pa.field("id", pa.string()),
                    pa.field("document", pa.string()),
                    pa.field("embedding", pa.list_(pa.float32(), list_size=self._embedding_dimension)),
                    pa.field("metadata", pa.string())
                ])
                logger.info(f"Inferred embedding dimension: {self._embedding_dimension}. Updated schema.")
                self.table = self.db.create_table(self.collection_name, schema=self.schema)
                logger.info(f"Created LanceDB table '{self.collection_name}' with inferred schema (dim={self._embedding_dimension}).")

            except Exception as inference_e:
                logger.error(f"Failed to create table with inferred schema: {inference_e}. Using generic schema.")
                # self.schema would be the one from __init__ without list_size if dimension was not known then
                self.table = self.db.create_table(self.collection_name, schema=self.schema)
                logger.warning(f"Created LanceDB table '{self.collection_name}' with generic schema (no fixed vector dimension).")
        else: # Dimension was known (or became known through other means), create with the current self.schema
            if not self.schema: # Should not happen if __init__ sets a fallback schema
                 raise RuntimeError("Schema is not defined, cannot create table.")
            self.table = self.db.create_table(self.collection_name, schema=self.schema)
            logger.info(f"Created LanceDB table '{self.collection_name}' using pre-defined schema (dim={self._embedding_dimension}).")


    def add(
        self,
        documents: List[str],
        metadatas: Optional[List[Optional[Dict[str, Any]]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        if not self.table:
            self._ensure_table_exists_with_data_for_schema_inference()
            if not self.table:
                logger.error("LanceDB table could not be initialized. Cannot add documents.")
                raise RuntimeError("LanceDB table not initialized after attempting creation.")

        if not documents:
            logger.debug("No documents provided to add.")
            return

        doc_ids: List[str] = []
        if ids:
            if len(ids) != len(documents):
                raise ValueError("Number of IDs must match number of documents if provided.")
            doc_ids = ids
        else:
            for doc_content in documents:
                doc_ids.append(hashlib.md5(doc_content.encode("utf-8")).hexdigest())

        processed_metadatas: List[str] = []
        if metadatas:
            if len(metadatas) != len(documents):
                raise ValueError("Number of metadatas must match number of documents if provided.")
            for meta in metadatas:
                processed_metadatas.append(json.dumps(meta) if meta else "{}")
        else:
            processed_metadatas = [json.dumps({}) for _ in documents]

        try:
            if not callable(self.embedder):
                raise TypeError("Embedder is not callable.")
            embeddings_list_of_lists = self.embedder(documents)
            if not embeddings_list_of_lists or len(embeddings_list_of_lists) != len(documents):
                raise ValueError("Embedder did not return the expected number of embeddings.")

            final_embeddings = []
            for emb_idx, emb in enumerate(embeddings_list_of_lists):
                current_emb_list: List[float]
                raw_emb = emb
                if hasattr(raw_emb, 'tolist'):
                    current_emb_list = raw_emb.tolist()
                elif isinstance(raw_emb, list) and all(isinstance(e_val, (float, int, np.float32, np.float64)) for e_val in raw_emb):
                    current_emb_list = [float(e_val) for e_val in raw_emb]
                else:
                    raise ValueError(f"Embedding for document {doc_ids[emb_idx]} is not a list of numbers or a numpy array: {type(raw_emb)}")

                if not self._embedding_dimension and emb_idx == 0: # First embedding and dimension was unknown
                    self._embedding_dimension = len(current_emb_list)
                    logger.info(f"Embedding dimension determined dynamically during first add: {self._embedding_dimension}. Schema might need update for strictness.")
                    # If self.schema was generic, update it if possible (complex if table already created with generic)
                    if self.schema.field("embedding").type.list_size is None : # Check if current schema is generic for embedding
                        self.schema = pa.schema([
                            pa.field("id", pa.string()), pa.field("document", pa.string()),
                            pa.field("embedding", pa.list_(pa.float32(), list_size=self._embedding_dimension)),
                            pa.field("metadata", pa.string())
                        ])
                        logger.info("Updated in-memory schema with dynamically found embedding dimension.")
                elif self._embedding_dimension and len(current_emb_list) != self._embedding_dimension:
                    raise ValueError(f"Embedding dimension mismatch for doc ID {doc_ids[emb_idx]}. Expected {self._embedding_dimension}, got {len(current_emb_list)}.")
                final_embeddings.append(current_emb_list)

        except Exception as e:
            error_message = (
                f"Embedding generation or validation failed in LanceDBVectorStore for collection "
                f"'{self.collection_name}' during 'add' operation. Error: {type(e).__name__}: {e}"
            )
            logger.error(error_message)
            raise RuntimeError(error_message) from e

        data_to_add = []
        for i in range(len(documents)):
            data_to_add.append({
                "id": doc_ids[i],
                "document": documents[i],
                "embedding": final_embeddings[i],
                "metadata": processed_metadatas[i],
            })

        if not data_to_add:
            logger.debug("No data prepared to add to LanceDB after processing.")
            return

        try:
            self.table.add(data_to_add)
            logger.info(f"Successfully added {len(data_to_add)} documents to LanceDB table '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to add data to LanceDB table '{self.collection_name}': {e}")
            raise RuntimeError(f"LanceDB table.add failed: {e}") from e


    def search(
        self,
        query_texts: List[str],
        n_results: int = 5,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> List[List[VectorStoreQueryResult]]:
        if not self.table:
            if self.collection_name in self.db.table_names():
                self.table = self.db.open_table(self.collection_name)
                logger.info(f"Opened table '{self.collection_name}' on demand for search.")
            else:
                logger.warning(f"LanceDB table '{self.collection_name}' is not initialized and does not exist. Cannot search documents.")
                return [[] for _ in query_texts]

        if not query_texts:
            return []

        all_query_results: List[List[VectorStoreQueryResult]] = []

        for query_text in query_texts:
            try:
                if not callable(self.embedder):
                    raise TypeError("Embedder is not callable.")
                query_embedding_list = self.embedder([query_text])
                if not query_embedding_list or not query_embedding_list[0]:
                    logger.error(f"Failed to embed query text (empty result from embedder): {query_text} in collection {self.collection_name}")
                    all_query_results.append([])
                    continue

                query_vector: List[float]
                raw_query_emb = query_embedding_list[0]
                if hasattr(raw_query_emb, 'tolist'):
                    query_vector = raw_query_emb.tolist()
                elif isinstance(raw_query_emb, list) and all(isinstance(e_val, (float, int, np.float32, np.float64)) for e_val in raw_query_emb):
                    query_vector = [float(e_val) for e_val in raw_query_emb]
                else:
                    raise ValueError(f"Query embedding is not a list of numbers or a numpy array: {type(raw_query_emb)}")

                if self._embedding_dimension and len(query_vector) != self._embedding_dimension:
                    logger.error(f"Query embedding dimension mismatch. Expected {self._embedding_dimension}, got {len(query_vector)}. Skipping query.")
                    all_query_results.append([])
                    continue

            except Exception as e:
                logger.error(f"Embedding generation failed for query '{query_text}': {e}")
                all_query_results.append([])
                continue

            search_query_builder = self.table.search(query_vector).limit(n_results)

            if filter_criteria:
                conditions = []
                for key, value in filter_criteria.items():
                    clean_key = key.replace("'", "''")
                    json_path = f"$.{clean_key}"
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "''")
                        conditions.append(f"json_extract(metadata, '{json_path}') = '{escaped_value}'")
                    elif isinstance(value, (int, float)):
                         conditions.append(f"json_extract(metadata, '{json_path}') = {value}")
                    elif isinstance(value, bool):
                        conditions.append(f"json_extract(metadata, '{json_path}') = {str(value).lower()}")
                    else:
                        logger.warning(f"Unsupported filter value type for key '{clean_key}': {type(value)}. Skipping this filter condition.")

                if conditions:
                    filter_string = " AND ".join(conditions)
                    try:
                        search_query_builder = search_query_builder.where(filter_string)
                        logger.debug(f"Applied filter to LanceDB search for query '{query_text}': {filter_string}")
                    except Exception as filter_e:
                        logger.error(f"Error applying filter string '{filter_string}' to LanceDB query: {filter_e}. Proceeding without filter.")

            try:
                lance_results = search_query_builder.to_list()
            except Exception as e:
                logger.error(f"LanceDB search execution failed for query '{query_text}': {e}")
                all_query_results.append([])
                continue

            current_query_results: List[VectorStoreQueryResult] = []
            for res_dict in lance_results:
                distance = res_dict.get("_distance", float('inf'))
                score = 1.0 / (1.0 + distance + 1e-9)

                metadata_dict: Optional[Dict[str, Any]] = None
                raw_metadata = res_dict.get("metadata")
                if isinstance(raw_metadata, str):
                    try:
                        metadata_dict = json.loads(raw_metadata)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse metadata JSON for ID {res_dict.get('id', 'N/A')}: {raw_metadata}")
                        metadata_dict = {"raw_metadata": raw_metadata, "error": "JSON parsing failed"}
                elif isinstance(raw_metadata, dict):
                    metadata_dict = raw_metadata

                current_query_results.append(
                    VectorStoreQueryResult(
                        id=str(res_dict.get("id", "")),
                        document=str(res_dict.get("document","")),
                        metadata=metadata_dict,
                        score=score
                    )
                )
            all_query_results.append(current_query_results)

        return all_query_results

    def reset(self) -> None:
        if not self.db:
            logger.error("LanceDB connection not initialized. Cannot reset.")
            try: # Attempt to reconnect if URI is available
                self.db = lancedb.connect(self.db_uri)
                logger.info(f"Reconnected to LanceDB at URI '{self.db_uri}' for reset.")
            except Exception as e:
                raise RuntimeError(f"LanceDB connection not initialized and failed to reconnect: {e}") from e


        logger.info(f"Attempting to reset LanceDB collection '{self.collection_name}'.")
        try:
            if self.collection_name in self.db.table_names():
                self.db.drop_table(self.collection_name)
                logger.info(f"Successfully dropped LanceDB table '{self.collection_name}'.")
            else:
                logger.info(f"LanceDB table '{self.collection_name}' does not exist. No need to drop.")

            if not self.schema:
                # This should ideally not happen if __init__ always defines a schema (even a generic one)
                # However, as a safeguard, try to re-initialize a generic schema if it's None.
                logger.warning("Schema was not defined prior to reset. Initializing a generic schema for table recreation.")
                self.schema = pa.schema([
                    pa.field("id", pa.string()), pa.field("document", pa.string()),
                    pa.field("embedding", pa.list_(pa.float32())), pa.field("metadata", pa.string())
                ])
                if self._embedding_dimension : # If dimension became known, use it
                     self.schema = pa.schema([
                        pa.field("id", pa.string()), pa.field("document", pa.string()),
                        pa.field("embedding", pa.list_(pa.float32(), list_size=self._embedding_dimension)),
                        pa.field("metadata", pa.string())
                    ])


            # Recreate the table using the stored/updated self.schema.
            # mode="overwrite" is crucial if the table might exist in some edge cases or if drop failed silently.
            self.table = self.db.create_table(self.collection_name, schema=self.schema, mode="overwrite")
            logger.info(f"Successfully recreated LanceDB table '{self.collection_name}' with schema after reset.")

        except Exception as e:
            logger.error(f"Error during reset of LanceDB table '{self.collection_name}': {e}")
            self.table = None # Table is in an uncertain state
            raise RuntimeError(f"Failed to reset LanceDB table: {e}") from e


    def __del__(self):
        # LanceDB connections are typically managed by the library.
        # Explicitly closing is usually not needed for local DBs.
        # If self.db were a remote client, .close() might be relevant.
        pass
