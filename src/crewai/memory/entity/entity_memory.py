from typing import Any, Dict, Optional

from pydantic import PrivateAttr

from crewai.memory.entity.entity_memory_item import EntityMemoryItem
from crewai.memory.memory import Memory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.utilities.paths import db_storage_path


class EntityMemory(Memory):
    """
    EntityMemory class for managing structured information about entities
    and their relationships.
    Inherits from the Memory class.
    """

    _memory_provider: Optional[str] = PrivateAttr()

    def __init__(
        self,
        crew=None,
        embedder_config: Optional[Dict[str, Any]] = None,
        storage_config: Optional[Dict[str, Any]] = None, # New config for RAGStorage
        storage=None # Existing storage instance option
    ):
        memory_provider = None
        if crew and hasattr(crew, "memory_config") and crew.memory_config is not None:
            memory_provider = crew.memory_config.get("provider")

        if memory_provider == "mem0":
            try:
                from crewai.memory.storage.mem0_storage import Mem0Storage # type: ignore
            except ImportError:
                raise ImportError(
                    "Mem0 is not installed. Please install it with `pip install mem0ai`."
                )
            # Mem0Storage might also need refactoring for storage_config if it uses RAG principles
            # For now, assuming its __init__ is compatible or will be updated separately.
            storage_to_use = Mem0Storage(type="entities", crew=crew)
        elif storage:
            storage_to_use = storage
        else:
            # Prepare default storage_config if not provided
            effective_storage_config = storage_config
            if not effective_storage_config:
                # Try to create a unique collection name using crew ID or role if available
                crew_identifier = "default"
                if crew:
                    if hasattr(crew, "id"): # Assuming crew might have an id
                        crew_identifier = str(crew.id)
                    # Add more specific identifiers if available, e.g. from agent passed to memory

                collection_name = f"entities_{crew_identifier}"
                default_persist_path = str(db_storage_path() / "memory" / "entities")

                effective_storage_config = {
                    "type": "chromadb", # Default to chromadb or make it configurable globally
                    "collection_name": collection_name,
                    "persist_path": default_persist_path,
                }

            storage_to_use = RAGStorage(
                storage_config=effective_storage_config,
                embedder_config=embedder_config,
                crew=crew, # RAGStorage might use crew for context/defaults
            )

        super().__init__(storage=storage_to_use)
        self._memory_provider = memory_provider

    def save(self, item: EntityMemoryItem) -> None:  # type: ignore
        """Saves an entity item into the configured storage."""
        if self._memory_provider == "mem0":
            data = f"""
            Remember details about the following entity:
            Name: {item.name}
            Type: {item.type}
            Entity Description: {item.description}
            """
        else:
            data = f"{item.name}({item.type}): {item.description}"

        # The metadata for RAGStorage should be Dict[str, Any]
        # item.metadata is already expected to be a dict.
        super().save(value=data, metadata=item.metadata or {})


    def reset(self) -> None:
        try:
            self.storage.reset()
        except Exception as e:
            raise Exception(f"An error occurred while resetting the entity memory: {e}")
