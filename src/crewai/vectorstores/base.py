from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class VectorStoreQueryResult:
    """
    Represents a single query result from a vector store.

    Attributes:
        id: The unique identifier of the retrieved document.
        document: The content of the retrieved document.
        metadata: A dictionary containing metadata associated with the document.
        score: The similarity score of the document to the query.
               (Higher scores generally indicate greater similarity).
    """
    id: str
    document: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    score: Optional[float] = None

class VectorStoreInterface(ABC):
    """
    Abstract Base Class for vector store implementations.

    This interface defines the common methods that concrete vector store
    adapters (e.g., for ChromaDB, SQLite-based stores) should implement.
    """

    @abstractmethod
    def __init__(self,
                 collection_name: str,
                 embedder_config: Optional[Dict[str, Any]] = None,
                 persist_path: Optional[str] = None,
                 **kwargs):
        """
        Initializes the vector store.

        Args:
            collection_name: Name of the collection or table to be used.
            embedder_config: Configuration dictionary for the embedding model.
                             Concrete implementations will use this to set up
                             their embedding generation mechanism.
            persist_path: Optional path for persistent storage, if applicable.
            **kwargs: Additional keyword arguments for specific implementations.
        """
        pass

    @abstractmethod
    def add(self,
            documents: List[str],
            metadatas: Optional[List[Optional[Dict[str, Any]]]] = None,
            ids: Optional[List[str]] = None) -> None:
        """
        Adds documents and their embeddings to the vector store.

        Args:
            documents: A list of document texts.
            metadatas: An optional list of metadata dictionaries, one for each document.
            ids: An optional list of unique identifiers for each document.
        """
        pass

    @abstractmethod
    def search(self,
               query_texts: List[str],
               n_results: int = 5,
               filter_criteria: Optional[Dict[str, Any]] = None) -> List[List[VectorStoreQueryResult]]:
        """
        Searches the vector store for documents similar to the query texts.

        Args:
            query_texts: A list of query texts.
            n_results: The number of similar documents to retrieve for each query.
            filter_criteria: An optional dictionary for metadata-based filtering.
                             The exact structure and interpretation of this dictionary
                             will depend on the concrete implementation.

        Returns:
            A list of lists of VectorStoreQueryResult objects. Each inner list
            corresponds to a query text and contains the top N results for that query.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Resets the specific collection/table in the vector store.
        This typically means deleting all entries within the collection.
        """
        pass
