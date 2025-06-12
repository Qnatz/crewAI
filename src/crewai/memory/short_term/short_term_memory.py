from typing import Any, Dict, Optional

from pydantic import PrivateAttr

from crewai.memory.memory import Memory
from crewai.memory.short_term.short_term_memory_item import ShortTermMemoryItem
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.utilities.paths import db_storage_path


class ShortTermMemory(Memory):
    """
    ShortTermMemory class for managing transient data related to immediate tasks
    and interactions.
    Inherits from the Memory class and utilizes an instance of a class that
    adheres to the Storage for data storage, specifically working with
    MemoryItem instances.
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
            # Assuming Mem0Storage has a compatible or will be updated __init__
            storage_to_use = Mem0Storage(type="short_term", crew=crew)
        elif storage:
            storage_to_use = storage
        else:
            effective_storage_config = storage_config
            if not effective_storage_config:
                crew_identifier = "default"
                if crew and hasattr(crew, "id"): # Assuming crew might have an id
                    crew_identifier = str(crew.id)

                collection_name = f"short_term_{crew_identifier}"
                default_persist_path = str(db_storage_path() / "memory" / "short_term")

                effective_storage_config = {
                    "type": "chromadb", # Default type
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

    def save(
        self,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None,
        agent: Optional[str] = None,
    ) -> None:
        item = ShortTermMemoryItem(data=value, metadata=metadata, agent=agent)
        if self._memory_provider == "mem0": # This logic specific to mem0 should ideally be within Mem0Storage.save
            # For now, keeping it here as per original structure.
            item_data_to_save = f"Remember the following insights from Agent run: {item.data}"
        else:
            item_data_to_save = item.data

        # Ensure metadata is a dict, even if None initially
        super().save(value=item_data_to_save, metadata=item.metadata or {}, agent=item.agent)


    def search(
        self,
        query: str,
        limit: int = 3,
        score_threshold: float = 0.35,
        filter_criteria: Optional[Dict[str, Any]] = None, # Added filter_criteria
        **kwargs # Allow other args
    ):
        # The parent Memory class's search method might not have all these params.
        # RAGStorage.search (which is self.storage here if not mem0) now has filter_criteria.
        if hasattr(self.storage, "search") and callable(getattr(self.storage, "search")):
            # Check if the storage object's search method can handle filter_criteria
            # This is a bit of a workaround for Python's dynamic typing.
            # A better solution would be for all storage types to adhere to a strict interface.
            try:
                return self.storage.search(
                    query=query,
                    limit=limit,
                    score_threshold=score_threshold,
                    filter_criteria=filter_criteria, # Pass it down
                    **kwargs
                ) # type: ignore
            except TypeError: # If the underlying search doesn't take filter_criteria or kwargs
                 return self.storage.search(
                    query=query,
                    limit=limit,
                    score_threshold=score_threshold
                ) # type: ignore
        else:
            # Fallback or raise error if storage doesn't have a compatible search
            raise NotImplementedError("The configured storage does not support the required search method parameters.")


    def reset(self) -> None:
        try:
            self.storage.reset()
        except Exception as e:
            raise Exception(
                f"An error occurred while resetting the short-term memory: {e}"
            )
