# mycrews/qrew/tools/chroma_logger.py
import os
import uuid
import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OnnxEmbeddingFunction # Added import
from typing import List, Optional, Dict, Any

class ChromaLogger:
    def __init__(self, collection_name: str = "qrew_system_logs", persist_directory: Optional[str] = None, onnx_model_dir_override: Optional[str] = None):
        if persist_directory is None:
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_script_dir, "..", "..", "..")
            base_persist_dir = os.path.join(project_root, "db", "chroma_storage_logger")
        else:
            base_persist_dir = persist_directory
        self.persist_directory = os.path.abspath(base_persist_dir)
        os.makedirs(self.persist_directory, exist_ok=True)

        self.onnx_embedding_function = None
        # Determine ONNX model directory path
        if onnx_model_dir_override:
            onnx_model_path = os.path.abspath(onnx_model_dir_override)
        else:
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_script_dir, "..", "..", "..")
            onnx_model_path = os.path.join(project_root, "models", "onnx")

        onnx_model_file_path = os.path.join(onnx_model_path, "model.onnx") # Path to the actual .onnx file
        if not os.path.exists(onnx_model_file_path):
             print(f"ChromaLogger: Warning - ONNX model file not found at {onnx_model_file_path}. Semantic log search may not work as expected.")
        else:
            try:
                # OnnxEmbeddingFunction typically takes the model_name which can be a path to the directory.
                self.onnx_embedding_function = OnnxEmbeddingFunction(model_name=onnx_model_path)
                print(f"ChromaLogger: OnnxEmbeddingFunction initialized with model directory: {onnx_model_path}")
            except Exception as e_ef:
                print(f"ChromaLogger: Warning - Failed to initialize OnnxEmbeddingFunction with model directory {onnx_model_path}: {e_ef}")
                self.onnx_embedding_function = None

        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(allow_reset=False)
            )
            if self.onnx_embedding_function:
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.onnx_embedding_function
                )
            else:
                self.collection = self.client.get_or_create_collection(name=collection_name)
                print(f"ChromaLogger: Warning - Collection '{collection_name}' created without an embedding function. Semantic search on log content will not be available.")
            print(f"ChromaLogger: Initialized with collection '{collection_name}' at {self.persist_directory}")
        except Exception as e:
            print(f"ChromaLogger: CRITICAL - Failed to initialize ChromaDB client or collection: {e}")
            self.client = None
            self.collection = None

    def log(
        self,
        content: str,
        stage: str = "unknown",
        log_type: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        if not self.collection:
            print("ChromaLogger: Collection not available. Cannot log.")
            return None

        custom_metadata = metadata or {}
        log_id = f"{stage}_{log_type}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.datetime.utcnow().isoformat()

        try:
            self.collection.add(
                ids=[log_id],
                documents=[content],
                metadatas=[{
                    "stage": stage,
                    "type": log_type,
                    "timestamp": timestamp,
                    "log_content_full": content,
                    **custom_metadata
                }]
            )
            return log_id
        except Exception as e:
            print(f"ChromaLogger: Error during log addition: {e}")
            return None

    def save_project_state(self, project_name: str, state: Dict[str, Any]) -> Optional[str]:
        if not self.collection:
            print("ChromaLogger: Collection not available. Cannot save project state.")
            return None

        state_id = f"state_{project_name}"
        timestamp = datetime.datetime.utcnow().isoformat()

        state_metadata = {
            "type": "project_state",
            "project_name": project_name,
            "timestamp": timestamp,
            **state
        }

        try:
            document_content = f"State snapshot for project: {project_name} at {timestamp}"
            self.collection.upsert(
                ids=[state_id],
                documents=[document_content],
                metadatas=[state_metadata]
            )
            return state_id
        except Exception as e:
            print(f"ChromaLogger: Error during save_project_state: {e}")
            return None

    def get_project_state(self, project_name: str) -> Optional[Dict[str, Any]]:
        if not self.collection:
            print("ChromaLogger: Collection not available. Cannot get project state.")
            return None

        state_id = f"state_{project_name}"
        try:
            result = self.collection.get(ids=[state_id], include=['metadatas'])
            if result and result.get("metadatas") and len(result.get("metadatas")) > 0:
                return result["metadatas"][0]
            return None
        except Exception as e:
            print(f"ChromaLogger: Error during get_project_state: {e}")
            return None

    def query_logs(self, query_texts: Optional[List[str]] = None, n_results: int = 5, where_filter: Optional[Dict[str, Any]] = None, include_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        if not self.collection:
            print("ChromaLogger: Collection not available. Cannot query logs.")
            return {}

        if include_fields is None:
            include_fields = ['metadatas', 'documents', 'distances']
        if self.collection.count() == 0: # Check if collection is empty
            # print("ChromaLogger: Log collection is empty.") # Commented out for less noise
            return {}
        try:
            return self.collection.query(
                query_texts=query_texts if query_texts else None,
                n_results=n_results,
                where=where_filter if where_filter else None,
                include=include_fields
            )
        except Exception as e:
            print(f"ChromaLogger: Error during query_logs: {e}")
            return {}

    def clear_all_logs_and_states(self, collection_name_to_clear: Optional[str] = None) -> None:
        if not self.client:
            print("ChromaLogger: Client not available. Cannot clear logs.")
            return

        name_to_clear = collection_name_to_clear if collection_name_to_clear else (self.collection.name if self.collection else None)
        if not name_to_clear:
            print("ChromaLogger: No collection name specified or available to clear.")
            return
        try:
            self.client.delete_collection(name=name_to_clear)
            if self.collection and self.collection.name == name_to_clear: # Recreate if it was the default
                self.collection = self.client.get_or_create_collection(name=name_to_clear)
            print(f"ChromaLogger: Collection '{name_to_clear}' cleared.")
        except Exception as e:
            print(f"ChromaLogger: Info/Error during clear_all_logs_and_states for '{name_to_clear}': {e}")
