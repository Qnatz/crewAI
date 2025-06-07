import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage
from crewai.utilities.paths import db_storage_path # For default persist_path

os.environ["TOKENIZERS_PARALLELISM"] = "false"  # removes logging from fastembed


class Knowledge(BaseModel):
    """
    Knowledge is a collection of sources and setup for the vector store to save and query relevant context.
    Args:
        sources: List[BaseKnowledgeSource] = Field(default_factory=list)
        storage_config: Optional[Dict[str, Any]] = Field(default=None)
        embedder_config: Optional[Dict[str, Any]] = None
        collection_name: Name for the knowledge collection.
    """

    sources: List[BaseKnowledgeSource] = Field(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)
    storage: Optional[KnowledgeStorage] = Field(default=None) # Will hold the configured KnowledgeStorage instance
    embedder_config: Optional[Dict[str, Any]] = Field(default=None)
    storage_config: Optional[Dict[str, Any]] = Field(default=None)
    collection_name: str # Made mandatory for clarity

    def __init__(
        self,
        collection_name: str, # Made collection_name a direct argument
        sources: List[BaseKnowledgeSource],
        embedder_config: Optional[Dict[str, Any]] = None,
        storage_config: Optional[Dict[str, Any]] = None,
        # storage: Optional[KnowledgeStorage] = None, # Removed direct storage injection from __init__ to force config use
        **data, # Pydantic data
    ):
        # Initialize Pydantic model fields first
        super().__init__(
            collection_name=collection_name,
            sources=sources,
            embedder_config=embedder_config,
            storage_config=storage_config,
            **data
        )

        # Prepare effective storage configuration
        effective_storage_config = self.storage_config
        if not effective_storage_config:
            default_persist_path = str(db_storage_path() / "knowledge_stores")
            effective_storage_config = {
                "type": "chromadb", # Default type
                "collection_name": self.collection_name,
                "persist_path": default_persist_path,
            }
        else: # Ensure collection_name from __init__ is in the config if provided
            effective_storage_config["collection_name"] = self.collection_name
            if "persist_path" not in effective_storage_config: # Add default persist_path if not specified
                 effective_storage_config["persist_path"] = str(db_storage_path() / "knowledge_stores" / self.collection_name)


        # The KnowledgeStorage class now takes storage_config and embedder_config
        self.storage = KnowledgeStorage(
            storage_config=effective_storage_config,
            embedder_config=self.embedder_config,
        )

        # self.storage.initialize_knowledge_storage() # This is now called within KnowledgeStorage.__init__ via _initialize_vector_store

    def query(
        self, query: List[str], results_limit: int = 3, score_threshold: float = 0.35
    ) -> List[Dict[str, Any]]:
        """
        Query across all knowledge sources to find the most relevant information.
        Returns the top_k most relevant chunks.

        Raises:
            ValueError: If storage is not initialized.
        """
        if self.storage is None: # Should not happen if __init__ completes
            raise ValueError("Storage is not initialized.")

        results = self.storage.search(
            query,
            limit=results_limit,
            score_threshold=score_threshold,
        )
        return results

    def add_sources(self):
        """Adds all configured sources to the knowledge storage."""
        if self.storage is None:
            raise ValueError("Storage is not initialized. Cannot add sources.")
        try:
            for source in self.sources:
                # KnowledgeStorage.save expects List[str] and List[Optional[Dict]]
                # BaseKnowledgeSource.add() should ideally call KnowledgeStorage.save()
                # This part might need review based on BaseKnowledgeSource.add() internal logic
                # Assuming BaseKnowledgeSource.add() now correctly uses the refactored KnowledgeStorage.save()
                source.storage = self.storage # Ensure source uses the configured storage
                source.add()
        except Exception as e:
            # Consider more specific error logging or handling
            raise Exception(f"Error adding sources to knowledge base '{self.collection_name}': {e}") from e


    def reset(self) -> None:
        if self.storage:
            self.storage.reset()
        else:
            raise ValueError("Storage is not initialized.")
