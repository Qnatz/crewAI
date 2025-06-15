import os
import numpy as np
import tensorflow as tf # Changed from tflite_runtime
import sentencepiece as spm

class USELiteEmbeddingTool:
    def __init__(self,
                 model_path=None,
                 spm_path=None):
        # Corrected base_path to go up to project root (crewAI/)
        # Assumes tools/ is one level deep from project root, and models/ is also one level deep.
        # If tools/ is in mycrews/qrew/tools, then base_path needs to go up more levels.
        # The user's example path was: os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        # Let's check the current structure.
        # __file__ (use_lite_embedding_tool.py) is in tools/
        # So, ../ is project root.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        self.model_path = model_path or os.path.join(base_path, "models/use_lite.tflite")
        self.spm_path = spm_path or os.path.join(base_path, "models/use_lite.spm.model")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"TFLite model not found at {self.model_path}")
        if not os.path.exists(self.spm_path):
            raise FileNotFoundError(f"SentencePiece model not found at {self.spm_path}")

        # Load SentencePiece tokenizer
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(self.spm_path)

        # Load TensorFlow Lite model
        try:
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
        except Exception as e:
            # It's good practice to log the model path in the error.
            print(f"Error initializing TFLite interpreter for {self.model_path}: {e}")
            self.interpreter = None # Or re-raise to prevent tool use

    def embed(self, text: str) -> np.ndarray:
        if self.interpreter is None:
            # Or raise an exception if the interpreter failed to load
            raise RuntimeError("TFLite interpreter is not available.")

        # The user's guide had a more complex encode function for batching.
        # For a single sentence, a simpler tokenization is fine,
        # but the model might expect specific input tensor shapes as per the guide's encode().
        # The original simpler version in the codebase was:
        # tokens = self.sp.encode(text)
        # input_array = np.array([tokens], dtype=np.int32)
        # self.interpreter.set_tensor(self.input_details[0]['index'], input_array)

        # Let's use the user's encode logic adapted for a single sentence,
        # or ensure the model can handle the simpler input.
        # The user's example `use_infer.py` implies a multi-input model:
        # input_ids, input_idxs, input_shape
        # This is different from the original USELiteEmbeddingTool which assumed a single input tensor.
        # The new `USELiteEmbeddingTool` provided by user has input_details and output_details.
        # The `use_infer.py` script has this encode function:
        # def encode(sentences):
        #     ids = [self.sp.EncodeAsIds(s) for s in sentences]
        #     values = [i for sub in ids for i in sub]
        #     indices = [[r, c] for r, row in enumerate(ids) for c in range(len(row))]
        #     shape = [len(ids), max(len(r) for r in ids)]
        #     return np.array(values, dtype=np.int32), np.array(indices, dtype=np.int32), np.array(shape, dtype=np.int32)
        # This suggests the model takes three inputs: values, indices, shape.

        # Adapting the user's encode function for a single sentence passed to this embed method:
        sentences = [text]
        ids = [self.sp.encode_as_ids(s) for s in sentences] # encode_as_ids is correct spm method
        values_data = [i for sub in ids for i in sub]
        indices_data = [[r, c] for r, row in enumerate(ids) for c in range(len(row))]
        shape_data = [len(ids), max(len(r) for r in ids) if ids and ids[0] else 0] # Handle empty text

        # Assuming input_details order matches: 0:values, 1:indices, 2:shape
        # This needs to be verified against the actual model's input details.
        # The user's use_infer.py script used:
        # input_ids = interpreter.get_input_details()[0]['index'] (for values)
        # input_idxs = interpreter.get_input_details()[1]['index'] (for indices)
        # input_shape = interpreter.get_input_details()[2]['index'] (for shape)

        # Let's assume the order is 'values', 'indices', 'shape' if model has 3 inputs
        # Or if it's the model from TF Hub page for USE Lite which often has one input for tokens.
        # The original code in the repo had:
        # self.input_index = self.interpreter.get_input_details()[0]['index']
        # And then used a simple np.array([tokens])
        # The user's new code for USELiteEmbeddingTool does not specify how it handles multiple inputs
        # in its `embed` method, only in the `use_infer.py` example.

        # Given the user's `USELiteEmbeddingTool` code only gets `input_details[0]['index']` implicitly
        # if we just set one tensor, let's stick to the single sentence, single tensor input
        # if the model from TF Hub (universal-sentence-encoder-lite/2) supports it.
        # The TF Hub page for lite models usually shows a single input for token IDs.
        # The three-input signature (values, indices, shape) is for models that handle sparse tensor inputs.
        # If `universal_encoder_lite.tflite` is the standard one, it takes one input.

        # Reverting to simpler input based on standard USE Lite TFLite models.
        # If this specific model version *requires* the three inputs, this will fail.
        tokens = self.sp.encode_as_ids(text)
        input_array = np.array([tokens], dtype=np.int32)

        self.interpreter.set_tensor(self.input_details[0]['index'], input_array)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        return output[0]  # Return 512-dimensional embedding

# For CLI/debugging (optional to keep in the actual tool file)
if __name__ == "__main__":
    # Test with a relative path assuming models/ is sibling to tools/ from project root
    project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    test_model_path = os.path.join(project_root_dir, "models/use_lite.tflite")
    test_spm_path = os.path.join(project_root_dir, "models/use_lite.spm.model")

    print(f"Attempting to load model from: {test_model_path}")
    print(f"Attempting to load SPM from: {test_spm_path}")

    tool = USELiteEmbeddingTool(model_path=test_model_path, spm_path=test_spm_path)
    if tool.interpreter:
        result = tool.embed("CrewAI agents are highly modular.")
        print(f"Embedding (first 10 dims): {result[:10]}")
        print(f"Embedding shape: {result.shape}")
    else:
        print("Failed to initialize USELiteEmbeddingTool interpreter.")
