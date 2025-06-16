import os
import numpy as np
import sentencepiece as spm
from ai_edge_litert.compiled_model import CompiledModel  # Use CompiledModel instead of LiteInterpreter

class TextEmbedder:
    def __init__(self, model_path=None, spm_path=None):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))
        self.model_path = model_path or os.path.join(base, "use_lite.tflite")
        self.spm_path = spm_path or os.path.join(base, "use_lite.spm.model")

        # Load tokenizer
        sp = spm.SentencePieceProcessor()
        sp.load(self.spm_path)
        self.sp = sp

        # Load model with ai_edge_litert
        self.model = CompiledModel(self.model_path)  # Use CompiledModel here

    def embed(self, text: str) -> np.ndarray:
        ids = self.sp.encode(text, out_type=int)
        input_data = np.array([ids], dtype=np.int32)
        outputs = self.model.run(input_data)
        return outputs[0]

if __name__ == "__main__":
    e = TextEmbedder()
    vec = e.embed("Hello LiteRT!")
    print("Embedding shape:", vec.shape)
    print("First 5 dims:", vec[:5])
