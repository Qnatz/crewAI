import os
import numpy as np
import sentencepiece as spm
import tflite_runtime.interpreter as tflite


class USELiteEmbeddingTool:
    def __init__(self, model_path=None, spm_path=None):
        # Determine absolute path to the project root (crewAI/)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

        # Set default model and tokenizer paths
        model_path = model_path or os.path.join(base_dir, "models/use_lite.tflite")
        spm_path = spm_path or os.path.join(base_dir, "models/use_lite.spm.model")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"TFLite model not found at {model_path}")
        if not os.path.exists(spm_path):
            raise FileNotFoundError(f"SentencePiece model not found at {spm_path}")

        # Load SentencePiece model
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(spm_path)

        try:
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_index = self.interpreter.get_input_details()[0]['index']
            self.output_index = self.interpreter.get_output_details()[0]['index']
        except Exception as e:
            raise RuntimeError(f"Failed to initialize TFLite interpreter: {e}")

    def embed(self, text: str) -> np.ndarray:
        """Convert text into vector embedding using USE Lite"""
        tokens = self.sp.encode(text)
        input_array = np.array([tokens], dtype=np.int32)

        self.interpreter.set_tensor(self.input_index, input_array)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_index)
        return output[0]


if __name__ == "__main__":
    tool = USELiteEmbeddingTool()
    text = "This is a test sentence."
    vector = tool.embed(text)
    print(f"Input: {text}")
    print(f"Embedding (first 10 dims): {vector[:10]}")
