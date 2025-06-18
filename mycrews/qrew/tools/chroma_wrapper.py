# mycrews/qrew/tools/chroma_wrapper.py
from .chroma_sanitizer import sanitize_metadata
from typing import List, Dict, Any
import chromadb # For type hinting chromadb.Collection

def safe_upsert(collection: chromadb.Collection, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
    """
    Sanitize metadata, then upsert to the provided ChromaDB collection.
    Logs and suppresses exceptions for resilience.
    """
    if not collection:
        print("[ChromaWrapper] Upsert failed: ChromaDB collection object not provided.")
        return

    if not (len(ids) == len(documents) == len(metadatas)):
        print("[ChromaWrapper] Upsert failed: Mismatch in lengths of ids, documents, or metadatas.")
        return

    sanitized_metadatas = [sanitize_metadata(m) for m in metadatas]

    try:
        # print(f"[ChromaWrapper] Upserting {len(documents)} documents to collection '{collection.name}'.")
        collection.upsert(ids=ids, documents=documents, metadatas=sanitized_metadatas)
        # print(f"[ChromaWrapper] Upsert successful for {len(documents)} documents to collection '{collection.name}'.")
    except Exception as e:
        # Consider logging the actual collection name if possible, e.g. collection.name
        print(f"[ChromaWrapper] Upsert to collection failed: {e}")


def safe_add(collection: chromadb.Collection, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
    """
    Sanitize metadata, then add to the provided ChromaDB collection.
    Logs and suppresses exceptions for resilience.
    """
    if not collection:
        print("[ChromaWrapper] Add failed: ChromaDB collection object not provided.")
        return

    if not (len(ids) == len(documents) == len(metadatas)):
        print("[ChromaWrapper] Add failed: Mismatch in lengths of ids, documents, or metadatas.")
        return

    sanitized_metadatas = [sanitize_metadata(m) for m in metadatas]

    try:
        # print(f"[ChromaWrapper] Adding {len(documents)} documents with IDs to collection '{collection.name}'.")
        collection.add(ids=ids, documents=documents, metadatas=sanitized_metadatas)
        # print(f"[ChromaWrapper] Add successful for {len(documents)} documents to collection '{collection.name}'.")
    except Exception as e:
        print(f"[ChromaWrapper] Add to collection failed: {e}")
