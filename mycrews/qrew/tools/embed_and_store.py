import onnxruntime as ort
from tokenizers import Tokenizer
import numpy as np
import os  # Add this for CPU count

# from objectbox import Store # No longer directly used here
# from objectbox.model import Entity, Id, Property, Model # No longer directly used here
# Keep local Entity and build_model if other local funcs depend on them,
# otherwise, they are managed by ONNXObjectBoxMemory.
# For this refactor, we'll assume they are no longer needed for the main script logic.
from .onnx_objectbox_memory import ONNXObjectBoxMemory, KnowledgeEntry as ONNXKnowledgeEntry

# Local KnowledgeEntry and build_model are no longer needed as ONNXObjectBoxMemory handles its own.
# Keeping them would require importing Entity, Id, Property, Model from objectbox.model.
# Removing them makes the script cleaner.

# ----------------------------
# ONNX & Tokenizer Setup
# ----------------------------

tokenizer = Tokenizer.from_file("models/onnx/tokenizer.json")

# Configure ONNX session to avoid thread warnings
options = ort.SessionOptions()
options.intra_op_num_threads = os.cpu_count() or 1  # Use all available cores
session = ort.InferenceSession("models/onnx/model.onnx", options)

def embed_text(text: str) -> np.ndarray:
    encoded = tokenizer.encode(text)
    ids = np.array([encoded.ids], dtype=np.int64)
    mask = np.array([encoded.attention_mask], dtype=np.int64)
    types = np.array([encoded.type_ids], dtype=np.int64)
    
    inputs = {
        "input_ids": ids,
        "attention_mask": mask,
        "token_type_ids": types
    }
    
    # Get token embeddings from model
    token_embeddings = session.run(None, inputs)[0][0]  # Shape: (seq_len, hidden_size)
    
    # Convert to sentence embedding using mean pooling
    return np.mean(token_embeddings, axis=0)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ----------------------------
# Main Logic
# ----------------------------

if __name__ == "__main__":
    # Rebuild store from scratch for dev/testing
    import shutil
    # Using the class method from ONNXObjectBoxMemory for removal is cleaner
    ONNXObjectBoxMemory.remove_store_files("objectbox-data")
    # shutil.rmtree("objectbox-data", ignore_errors=True) # Old way

    onnx_memory = ONNXObjectBoxMemory(store_path="objectbox-data") # New

    try:
        # Local embed_text is used for generating embeddings
        def add_knowledge(text): # Modified function
            vec = embed_text(text).astype(np.float32) # Uses local embed_text
            onnx_memory.add_knowledge(text, vec) # New: use the memory class method

        def search(query, top_k=3): # Modified function
            q_vec = embed_text(query).astype(np.float32) # Uses local embed_text
            # Use the public vector_query method from ONNXObjectBoxMemory
            results = onnx_memory.vector_query(query_vector=q_vec, limit=top_k)
            # vector_query returns a list of dicts: [{'content': str, 'score': float}, ...]
            # Adapt this to the old return format if needed, or use it directly.
            # For this script, let's print directly from the new format.
            return results # Return the list of dicts

        # Demo entries
        add_knowledge("Python is a programming language.")
        add_knowledge("Kotlin is used for Android development.")
        add_knowledge("ObjectBox is a NoSQL database for mobile apps.")

        print("\nSearch results for 'What is used for mobile databases?'")
        # search now returns list of dicts [{'content': str, 'score': float}, ...]
        results = search("What is used for mobile databases?")
        for res in results:
            print(f"{res['score']:.4f} → {res['content']}")
            
    finally:
        # Use the class method from ONNXObjectBoxMemory to close the specific store instance
        ONNXObjectBoxMemory.close_store_instance("objectbox-data")
