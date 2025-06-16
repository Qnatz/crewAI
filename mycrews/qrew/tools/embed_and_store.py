import onnxruntime as ort
from tokenizers import Tokenizer
import numpy as np
import os  # Add this for CPU count

from objectbox import Store
from objectbox.model import Entity, Id, Property, Model

# ----------------------------
# Define Entity Properly
# ----------------------------

@Entity()
class KnowledgeEntry:
    id = Id()
    text = Property(str)
    embedding = Property(bytes)

def build_model():
    model = Model()
    model.entity(KnowledgeEntry)
    return model

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
    shutil.rmtree("objectbox-data", ignore_errors=True)

    store = None
    try:
        store = Store(build_model(), directory="objectbox-data")
        box = store.box(KnowledgeEntry)

        def add_knowledge(text):
            vec = embed_text(text).astype(np.float32)
            entry = KnowledgeEntry()
            entry.text = text
            entry.embedding = vec.tobytes()
            box.put(entry)

        def search(query, top_k=3):
            q_vec = embed_text(query).astype(np.float32)
            scored = []
            for entry in box.get_all():
                vec = np.frombuffer(entry.embedding, dtype=np.float32)
                scored.append((cosine_sim(q_vec, vec), entry.text))
            return sorted(scored, key=lambda x: x[0], reverse=True)[:top_k]

        # Demo entries
        add_knowledge("Python is a programming language.")
        add_knowledge("Kotlin is used for Android development.")
        add_knowledge("ObjectBox is a NoSQL database for mobile apps.")

        print("\nSearch results for 'What is used for mobile databases?'")
        for score, txt in search("What is used for mobile databases?"):
            print(f"{score:.4f} → {txt}")
            
    finally:
        if store:
            store.close()
