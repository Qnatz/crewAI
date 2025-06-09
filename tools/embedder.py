import numpy as np
import tflite_runtime.interpreter as tflite
from transformers import AutoTokenizer

MODEL_PATH = "models/embedding_model.tflite" # Adjusted path

# Placeholder for TFLite model initialization
# In a real scenario, ensure the model exists and is loaded correctly.
try:
    interp = tflite.Interpreter(model_path=MODEL_PATH)
    interp.allocate_tensors()
    inp_idx = interp.get_input_details()[0]["index"]
    out_idx = interp.get_output_details()[0]["index"]
except ValueError as e:
    # This will likely happen if the model file doesn't exist or is invalid
    print(f"Error initializing TFLite interpreter: {e}")
    print(f"Please ensure '{MODEL_PATH}' is a valid TFLite model.")
    # Fallback to dummy values if model loading fails, to allow basic script execution
    # This is for development purposes only; a real model is needed for functionality.
    class DummyInterpreter:
        def set_tensor(self, inp_idx, data): pass
        def invoke(self): pass
        def get_tensor(self, out_idx): return np.random.rand(1, 384).astype(np.float32) # Match dimension

    interp = DummyInterpreter()
    inp_idx = 0
    out_idx = 0

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def embed(texts: list[str]) -> list[np.ndarray]:
    embs = []
    for t in texts:
        toks = tokenizer(t, padding="max_length", truncation=True, max_length=128, return_tensors="np")
        # Ensure input_ids are of the correct type (usually int32 or int64)
        input_ids = toks["input_ids"].astype(np.int32)
        interp.set_tensor(inp_idx, input_ids)
        interp.invoke()
        vec = interp.get_tensor(out_idx).squeeze()
        # L2-normalize
        vec_norm = np.linalg.norm(vec)
        if vec_norm == 0: # Avoid division by zero
            vec = np.zeros_like(vec, dtype=np.float32)
        else:
            vec = vec / vec_norm
        embs.append(vec)
    return embs
