import unittest
from unittest.mock import patch, MagicMock, ANY
import numpy as np
from pathlib import Path
import hashlib
import json
import logging
from typing import List, Dict, Any, Optional

# Assuming these can be imported from their new locations
from crewai.vectorstores.base import VectorStoreInterface, VectorStoreQueryResult
from crewai.vectorstores.sqlite_store import SQLiteVectorStore, EnhancedSQLiteDB
# EmbeddingConfigurator will be mocked where its direct output is needed.

# Disable most logging for tests to keep output clean
logging.basicConfig(level=logging.CRITICAL)

class TestSQLiteVectorStore(unittest.TestCase):

    def setUp(self):
        self.collection_name = "test_sqlite_collection"
        self.persist_path = "./test_sqlite_dbs"
        self.embedder_config = {"provider": "mock"}

        # Clean up any old test dbs
        self.test_db_dir = Path(self.persist_path)
        if self.test_db_dir.exists():
            for f in self.test_db_dir.glob(f"{self.collection_name.replace('-', '_')}.db*"):
                f.unlink()

    def tearDown(self):
        # Clean up test dbs after tests
        if self.test_db_dir.exists():
            for f in self.test_db_dir.glob(f"{self.collection_name.replace('-', '_')}.db*"):
                f.unlink()
            # Attempt to remove directory if empty
            try:
                self.test_db_dir.rmdir()
            except OSError:
                pass # Directory not empty, or other error - fine for teardown

    @patch('crewai.vectorstores.sqlite_store.EnhancedSQLiteDB')
    @patch('crewai.vectorstores.sqlite_store.EmbeddingConfigurator')
    def test_initialize_sqlite_store(self, MockEmbeddingConfigurator, MockEnhancedSQLiteDB):
        mock_embedder_instance = MagicMock()
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = mock_embedder_instance

        store = SQLiteVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )

        MockEmbeddingConfigurator.return_value.configure_embedder.assert_called_once_with(config=self.embedder_config)
        self.assertEqual(store.embedder, mock_embedder_instance)

        expected_db_path = Path(self.persist_path) / f"{self.collection_name.replace('-', '_')}.db"
        MockEnhancedSQLiteDB.assert_called_once_with(
            db_path=expected_db_path,
            table_name=self.collection_name.replace('-', '_')
        )
        self.assertEqual(store.db, MockEnhancedSQLiteDB.return_value)

    @patch('crewai.vectorstores.sqlite_store.EnhancedSQLiteDB')
    @patch('crewai.vectorstores.sqlite_store.EmbeddingConfigurator')
    def test_add_documents_to_sqlite(self, MockEmbeddingConfigurator, MockEnhancedSQLiteDB):
        mock_embedder = MagicMock()
        # Simulate embedding generation: list of lists of floats
        mock_embedder.return_value = [[0.1, 0.2], [0.3, 0.4]]
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = mock_embedder

        mock_db_instance = MockEnhancedSQLiteDB.return_value

        store = SQLiteVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )
        store.db = mock_db_instance # Inject mock db

        documents = ["doc1 content", "doc2 content"]
        metadatas = [{"source": "s1"}, {"source": "s2"}]
        ids = ["id1", "id2"]

        store.add(documents=documents, metadatas=metadatas, ids=ids)

        mock_embedder.assert_called_once_with(documents)

        # Check that store_embeddings was called on the mock_db_instance
        args, kwargs = mock_db_instance.store_embeddings.call_args
        self.assertEqual(kwargs['item_ids'], ids)
        self.assertEqual(kwargs['contents'], documents)
        self.assertTrue(all(isinstance(e, np.ndarray) for e in kwargs['embeddings']))
        self.assertEqual(len(kwargs['embeddings']), 2)
        self.assertEqual(kwargs['metadatas'], metadatas)

        # Test with no IDs (auto-generated)
        mock_db_instance.store_embeddings.reset_mock()
        mock_embedder.reset_mock()
        expected_ids_hashed = [hashlib.md5(doc.encode()).hexdigest() for doc in documents]

        store.add(documents=documents, metadatas=metadatas)

        mock_embedder.assert_called_once_with(documents)
        args, kwargs = mock_db_instance.store_embeddings.call_args
        self.assertEqual(kwargs['item_ids'], expected_ids_hashed)


    @patch('crewai.vectorstores.sqlite_store.EnhancedSQLiteDB')
    @patch('crewai.vectorstores.sqlite_store.EmbeddingConfigurator')
    def test_search_documents_in_sqlite(self, MockEmbeddingConfigurator, MockEnhancedSQLiteDB):
        mock_embedder = MagicMock()
        # Simulate query embedding generation
        mock_embedder.return_value = [[0.1, 0.2]] # Embedding for "query1"
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = mock_embedder

        mock_db_instance = MockEnhancedSQLiteDB.return_value
        # Simulate DB returning results
        mock_db_instance.retrieve_similar_items.return_value = [
            {"id": "res_id1", "document": "res_doc1", "metadata": {"src": "db"}, "score": 0.9}
        ]

        store = SQLiteVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )
        store.db = mock_db_instance

        query_texts = ["query1"]
        filter_criteria = {"source": "s1"}
        results = store.search(query_texts=query_texts, n_results=1, filter_criteria=filter_criteria)

        mock_embedder.assert_called_once_with(query_texts)

        args, kwargs = mock_db_instance.retrieve_similar_items.call_args
        self.assertTrue(np.allclose(kwargs['query_embedding'], np.array([0.1, 0.2], dtype=np.float32)))
        self.assertEqual(kwargs['top_k'], 1)
        self.assertEqual(kwargs['filter_criteria'], filter_criteria)

        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]), 1)
        self.assertIsInstance(results[0][0], VectorStoreQueryResult)
        self.assertEqual(results[0][0].id, "res_id1")
        self.assertEqual(results[0][0].score, 0.9)

    @patch('crewai.vectorstores.sqlite_store.EnhancedSQLiteDB')
    @patch('crewai.vectorstores.sqlite_store.EmbeddingConfigurator')
    def test_search_documents_embedding_failure(self, MockEmbeddingConfigurator, MockEnhancedSQLiteDB):
        mock_embedder = MagicMock()
        mock_embedder.side_effect = Exception("Embedding API down")
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = mock_embedder

        store = SQLiteVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )
        store.db = MockEnhancedSQLiteDB.return_value # Not actually used if embedding fails first

        with self.assertLogs(logger='crewai.vectorstores.sqlite_store', level='ERROR') as cm:
            results = store.search(query_texts=["query1"])

        self.assertTrue(any("Embedding generation failed" in log_msg for log_msg in cm.output))
        self.assertEqual(results, [[]]) # Should return empty list for the failed query

    @patch('crewai.vectorstores.sqlite_store.EnhancedSQLiteDB')
    @patch('crewai.vectorstores.sqlite_store.EmbeddingConfigurator')
    def test_reset_sqlite_store(self, MockEmbeddingConfigurator, MockEnhancedSQLiteDB):
        MockEmbeddingConfigurator.return_value.configure_embedder.return_value = MagicMock()
        mock_db_instance = MockEnhancedSQLiteDB.return_value

        store = SQLiteVectorStore(
            collection_name=self.collection_name,
            embedder_config=self.embedder_config,
            persist_path=self.persist_path
        )
        store.db = mock_db_instance

        store.reset()
        mock_db_instance.clear_table.assert_called_once()

if __name__ == '__main__':
    unittest.main()
