import unittest
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
import hashlib
import logging
from typing import List, Dict, Any, Optional

# Assuming these can be imported
from crewai.vectorstores.base import VectorStoreInterface, VectorStoreQueryResult
from crewai.vectorstores.chromadb_store import ChromaDBVectorStore
# EmbeddingConfigurator will be mocked. ChromaDB client/collection will be mocked.

# Disable most logging for tests
logging.basicConfig(level=logging.CRITICAL)

class TestChromaDBVectorStore(unittest.TestCase):

    def setUp(self):
        self.collection_name = "test_chroma_collection"
        self.persist_path = "./test_chroma_dbs" # Chroma creates a directory here
        self.embedder_config = {"provider": "mock_chroma"}

        # Clean up any old test dbs (directories for Chroma)
        self.test_db_dir = Path(self.persist_path)
        # No specific file, Chroma manages its own directory structure.
        # We'd typically mock PersistentClient so it doesn't write to disk in unit tests.

    @patch('crewai.vectorstores.chromadb_store.chromadb.PersistentClient')
    @patch('crewai.vectorstores.chromadb_store.EmbeddingConfigurator')
    def test_initialize_chromadb_store(self, MockEmbeddingConfigurator, MockPersistentClient):
        mock_embedder_function_instance = MagicMock() # This should be an EmbeddingFunction for Chroma
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = mock_embedder_function_instance

        mock_client_instance = MockPersistentClient.return_value
        mock_collection_instance = MagicMock()
        mock_collection_instance.metadata = {"hnsw:space": "cosine"} # Simulate metadata for score calculation
        mock_client_instance.get_or_create_collection.return_value = mock_collection_instance

        store = ChromaDBVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )

        MockPersistentClient.assert_called_once_with(path=str(Path(self.persist_path)))
        MockEmbeddingConfigurator.return_value.configure_embedder.assert_called_once_with(config=self.embedder_config)

        mock_client_instance.get_or_create_collection.assert_called_once_with(
            name=self.collection_name,
            embedding_function=mock_embedder_function_instance
        )
        self.assertEqual(store.client, mock_client_instance)
        self.assertEqual(store.collection, mock_collection_instance)
        self.assertEqual(store._space, "cosine") # Check if space was read

    @patch('crewai.vectorstores.chromadb_store.chromadb.PersistentClient')
    @patch('crewai.vectorstores.chromadb_store.EmbeddingConfigurator')
    def test_add_documents_to_chromadb(self, MockEmbeddingConfigurator, MockPersistentClient):
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = MagicMock()
        mock_client_instance = MockPersistentClient.return_value
        mock_collection_instance = MagicMock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection_instance

        store = ChromaDBVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )

        documents = ["doc1 content", "doc2 content"]
        metadatas = [{"source": "s1"}, {"source": "s2"}]
        ids = ["id1", "id2"]

        store.add(documents=documents, metadatas=metadatas, ids=ids)

        mock_collection_instance.upsert.assert_called_once_with(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        # Test with auto-generated IDs
        mock_collection_instance.upsert.reset_mock()
        expected_ids_hashed = [hashlib.md5(doc.encode()).hexdigest() for doc in documents]
        store.add(documents=documents, metadatas=metadatas) # ids=None

        mock_collection_instance.upsert.assert_called_once_with(
            ids=expected_ids_hashed,
            documents=documents,
            metadatas=metadatas
        )

    @patch('crewai.vectorstores.chromadb_store.chromadb.PersistentClient')
    @patch('crewai.vectorstores.chromadb_store.EmbeddingConfigurator')
    def test_search_documents_in_chromadb(self, MockEmbeddingConfigurator, MockPersistentClient):
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = MagicMock()
        mock_client_instance = MockPersistentClient.return_value
        mock_collection_instance = MagicMock()
        # Simulate collection metadata for score calculation
        mock_collection_instance.metadata = {"hnsw:space": "cosine"} # Important for score conversion
        mock_client_instance.get_or_create_collection.return_value = mock_collection_instance

        # Simulate ChromaDB query response
        chroma_response = {
            "ids": [["res_id1", "res_id2"]],
            "documents": [["res_doc1", "res_doc2"]],
            "metadatas": [[{"src": "db1"}, {"src": "db2"}]],
            "distances": [[0.1, 0.2]] # Cosine distances (0=identical, 1=orthogonal, 2=opposite)
        }
        mock_collection_instance.query.return_value = chroma_response

        store = ChromaDBVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )
        store._space = "cosine" # Explicitly set for test if not read from metadata mock

        query_texts = ["query1"]
        filter_criteria = {"source": "s1"}
        results = store.search(query_texts=query_texts, n_results=2, filter_criteria=filter_criteria)

        mock_collection_instance.query.assert_called_once_with(
            query_texts=query_texts,
            n_results=2,
            where=filter_criteria
        )

        self.assertEqual(len(results), 1) # One list for one query
        self.assertEqual(len(results[0]), 2) # Two results in that list
        self.assertIsInstance(results[0][0], VectorStoreQueryResult)
        self.assertEqual(results[0][0].id, "res_id1")
        self.assertEqual(results[0][0].document, "res_doc1")
        self.assertEqual(results[0][0].metadata, {"src": "db1"})
        self.assertAlmostEqual(results[0][0].score, 1.0 - 0.1) # Score = 1 - cosine_distance

        self.assertEqual(results[0][1].id, "res_id2")
        self.assertAlmostEqual(results[0][1].score, 1.0 - 0.2)

    @patch('crewai.vectorstores.chromadb_store.chromadb.PersistentClient')
    @patch('crewai.vectorstores.chromadb_store.EmbeddingConfigurator')
    def test_search_documents_query_failure_in_chromadb(self, MockEmbeddingConfigurator, MockPersistentClient):
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = MagicMock()
        mock_client_instance = MockPersistentClient.return_value
        mock_collection_instance = MagicMock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection_instance

        # Simulate ChromaDB query raising an exception (e.g. embedding function fails)
        mock_collection_instance.query.side_effect = Exception("Chroma query failed")

        store = ChromaDBVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )

        with self.assertLogs(logger='crewai.vectorstores.chromadb_store', level='ERROR') as cm:
            results = store.search(query_texts=["query1"])

        self.assertTrue(any("Error querying ChromaDB collection" in log_msg for log_msg in cm.output))
        self.assertEqual(results, [[]]) # Should return empty list for the failed query

    @patch('crewai.vectorstores.chromadb_store.chromadb.PersistentClient')
    @patch('crewai.vectorstores.chromadb_store.EmbeddingConfigurator')
    def test_reset_chromadb_store(self, MockEmbeddingConfigurator, MockPersistentClient):
        mock_embed_func = MagicMock()
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = mock_embed_func

        mock_client_instance = MockPersistentClient.return_value
        mock_collection_instance = MagicMock() # Original collection
        mock_new_collection_instance = MagicMock() # Collection after reset

        # First call to get_or_create_collection returns original, second returns new
        mock_client_instance.get_or_create_collection.side_effect = [
            mock_collection_instance,
            mock_new_collection_instance
        ]

        store = ChromaDBVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )

        store.reset()

        mock_client_instance.delete_collection.assert_called_once_with(name=self.collection_name)
        # Check get_or_create_collection was called again after delete
        self.assertEqual(mock_client_instance.get_or_create_collection.call_count, 2)
        self.assertEqual(store.collection, mock_new_collection_instance)


if __name__ == '__main__':
    unittest.main()
