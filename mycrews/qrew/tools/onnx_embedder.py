# mycrews/qrew/tools/onnx_embedder.py
import numpy as np
from typing import List

# Import the embed_text function from the existing embed_and_store.py
# Also import the session and tokenizer to check their status, as embed_text relies on them.
try:
    from .embed_and_store import embed_text as actual_onnx_embed_function
    # It's better to have a status function in embed_and_store.py,
    # but for now, we'll assume if the import of embed_text works,
    # then embed_text itself will handle internal readiness of session/tokenizer.
    EMBEDDING_SYSTEM_IMPORTED_SUCCESSFULLY = True
    print("ONNXEmbedder (wrapper): Successfully imported 'embed_text' from .embed_and_store.")
except ImportError as e:
    print(f"ONNXEmbedder (wrapper): CRITICAL - Failed to import 'embed_text' from .embed_and_store: {e}. This embedder will not function.")
    actual_onnx_embed_function = None
    EMBEDDING_SYSTEM_IMPORTED_SUCCESSFULLY = False

class ONNXEmbedder:
    def __init__(self):
        """
        Wrapper for the ONNX embedding logic in embed_and_store.py.
        Initialization of the actual ONNX model and tokenizer happens
        within embed_and_store.py's global scope when it's first imported.
        """
        if not EMBEDDING_SYSTEM_IMPORTED_SUCCESSFULLY:
            raise ImportError("ONNXEmbedder cannot function: 'embed_text' from .embed_and_store could not be imported.")

        if not callable(actual_onnx_embed_function):
             raise ImportError("ONNXEmbedder cannot function: 'actual_onnx_embed_function' is not callable after import.")
        print("ONNXEmbedder (wrapper) initialized.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not EMBEDDING_SYSTEM_IMPORTED_SUCCESSFULLY:
            print("ONNXEmbedder (wrapper): Underlying embedding system not imported. Returning empty embeddings for documents.")
            return [[] for _ in texts]

        embeddings = []
        for text_item in texts:
            try:
                np_embedding = actual_onnx_embed_function(text_item)
                if isinstance(np_embedding, np.ndarray) and np_embedding.any():
                    embeddings.append(np_embedding.tolist())
                else:
                    # embed_text in embed_and_store.py returns np.zeros if session/tokenizer is None
                    # So, an array of zeros means the underlying system wasn't ready or text was empty.
                    print(f"ONNXEmbedder (wrapper): Warning - received zero or invalid embedding for document item: '{text_item[:50]}...'")
                    embeddings.append([])
            except Exception as e:
                print(f"ONNXEmbedder (wrapper): Error embedding document item: '{text_item[:50]}...': {e}")
                embeddings.append([])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        if not EMBEDDING_SYSTEM_IMPORTED_SUCCESSFULLY:
            print("ONNXEmbedder (wrapper): Underlying embedding system not imported. Returning empty embedding for query.")
            return []

        try:
            np_embedding = actual_onnx_embed_function(text)
            if isinstance(np_embedding, np.ndarray) and np_embedding.any():
                return np_embedding.tolist()
            else:
                # embed_text in embed_and_store.py returns np.zeros if session/tokenizer is None
                print(f"ONNXEmbedder (wrapper): Warning - received zero or invalid embedding for query: '{text[:50]}...'")
                return []
        except Exception as e:
            print(f"ONNXEmbedder (wrapper): Error embedding query '{text[:50]}...': {e}")
            return []
