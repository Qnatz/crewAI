import unittest
import os
import shutil
from mycrews.qrew.tools.knowledge_base_tool import KnowledgeBaseTool
from tools.objectbox_memory import ObjectBoxMemory

# Define a test-specific path for the ObjectBox store
TEST_DB_PATH = "test_db_kb_tool"

class TestKnowledgeBaseTool(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up for all tests in this class."""
        # Ensure the test DB directory is clean before starting
        if os.path.exists(TEST_DB_PATH):
            shutil.rmtree(TEST_DB_PATH)
        os.makedirs(TEST_DB_PATH, exist_ok=True)

        # Initialize ObjectBoxMemory with the test path and populate it
        cls.memory = ObjectBoxMemory(store_path_override=TEST_DB_PATH)
        cls.sample_data = [
            "CrewAI is a framework for orchestrating role-playing, autonomous AI agents.",
            "ObjectBox is an embedded database for mobile and IoT devices.",
            "The capital of France is Paris."
        ]
        for text in cls.sample_data:
            cls.memory.save(text) # This will use the actual embedder

        # Pass the configured memory instance to the tool
        cls.kb_tool = KnowledgeBaseTool(memory_instance=cls.memory)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in this class."""
        # Close the store and remove the test DB directory
        if hasattr(cls, 'memory') and cls.memory._store:
            ObjectBoxMemory.close_store() # Important to close before deleting files

        if os.path.exists(TEST_DB_PATH):
            shutil.rmtree(TEST_DB_PATH)

    def test_query_existing_data_crewai(self):
        """Test querying for data that exists (CrewAI)."""
        question = "What is CrewAI?"
        response = self.kb_tool._run(question)
        self.assertIn("CrewAI is a framework", response)

    def test_query_existing_data_objectbox(self):
        """Test querying for data that exists (ObjectBox)."""
        question = "Tell me about ObjectBox."
        response = self.kb_tool._run(question)
        self.assertIn("ObjectBox is an embedded database", response)

    def test_query_existing_data_paris(self):
        """Test querying for data that exists (Paris)."""
        question = "What is the capital of France?"
        response = self.kb_tool._run(question)
        self.assertIn("capital of France is Paris", response)

    def test_query_non_existent_data(self):
        """Test querying for data that does not exist."""
        question = "What is the color of the sky on Mars?"
        response = self.kb_tool._run(question)
        self.assertEqual(response, "No relevant information found in the knowledge base.")

    def test_query_with_dict_input(self):
        """Test querying using a dictionary input structure."""
        question_dict = {"question": {"description": "Explain CrewAI"}}
        response = self.kb_tool._run(question_dict)
        self.assertIn("CrewAI is a framework", response)

    def test_query_with_dict_input_direct_description(self):
        """Test querying using a dictionary input structure with direct description."""
        question_dict = {"description": "Describe ObjectBox"}
        response = self.kb_tool._run(question_dict)
        self.assertIn("ObjectBox is an embedded database", response)

if __name__ == '__main__':
    unittest.main()
