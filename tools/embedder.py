import numpy as np
from mycrews.qrew.tools.use_lite_embedding_tool import USELiteEmbeddingTool

# TODO: The USELiteEmbeddingTool is expected to load the models automatically.
# We need to confirm if it also handles L2 normalization.
# For now, the L2 normalization from the original embed function is kept.

def embed(texts: list[str]) -> list[np.ndarray]:
    embs = []
    # Instantiate the tool within the function scope if it's lightweight,
    # or outside if it's heavy to initialize and meant to be reused.
    # Assuming it's okay to instantiate per call for now.
    embedding_tool = USELiteEmbeddingTool()

    for t in texts:
        # The USELiteEmbeddingTool.embed method is assumed to take a single string
        # and return a numpy array (the embedding vector).
        vec = embedding_tool.embed(t) # This should return a np.ndarray

        # Ensure vec is a numpy array (USELiteEmbeddingTool.embed should guarantee this)
        if not isinstance(vec, np.ndarray):
            # This case should ideally not happen if USELiteEmbeddingTool works as expected.
            # If it can return None or other types, error handling or conversion is needed.
            print(f"Warning: Embedding for text '{t[:30]}...' is not a numpy array. Got {type(vec)}. Skipping normalization.")
            # Potentially append a zero vector or handle as an error
            embs.append(np.zeros(embedding_tool.DIMENSION, dtype=np.float32) if hasattr(embedding_tool, 'DIMENSION') else np.array([])) # Fallback if dimension is known
            continue

        # L2-normalize
        vec_norm = np.linalg.norm(vec)
        if vec_norm == 0: # Avoid division by zero
            # It's possible for an embedding to be all zeros, especially for empty or out-of-vocab inputs.
            # In such cases, the normalized vector should also be all zeros.
            vec = np.zeros_like(vec, dtype=np.float32)
        else:
            vec = vec / vec_norm
        embs.append(vec)
    return embs
