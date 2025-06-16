import numpy as np
import sentencepiece as spm
import tensorflow as tf
import os


class USELiteEmbedder:
    def __init__(self,
                 model_path="models/use_lite.tflite",
                 spm_path="models/use_lite.spm.model"):

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"TFLite model not found: {model_path}")
        if not os.path.exists(spm_path):
            raise FileNotFoundError(f"SentencePiece model not found: {spm_path}")

        self.sp = spm.SentencePieceProcessor()
        self.sp.load(spm_path)

        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        self.input_index = input_details[0]["index"]
        self.output_index = output_details[0]["index"]

    def preprocess(self, text):
        # Encode using SentencePiece model
        pieces = self.sp.encode(text, out_type=int)
        return np.array([pieces], dtype=np.int32)

    def embed(self, text):
        input_data = self.preprocess(text)

        self.interpreter.set_tensor(self.input_index, input_data)
        self.interpreter.invoke()

        embedding = self.interpreter.get_tensor(self.output_index)
        return embedding[0]  # 1D embedding

    def embed_batch(self, texts):
        return [self.embed(text) for text in texts]


if __name__ == "__main__":
    embedder = USELiteEmbedder()
    print("Embedding:", embedder.embed("CrewAI agents can now embed text locally."))
