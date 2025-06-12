import numpy as np
import tensorflow as tf

# Path to the TFLite model
TFLITE_MODEL_PATH = "models/text_embedder_e5.tflite"  # Adjust if needed

# Load TFLite model and allocate tensors
interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Print model input/output info
print("Input:", input_details)
print("Output:", output_details)

# 🔤 Prepare dummy input: shape and dtype must match model input
sample_text = "test sentence"
input_len = input_details[0]['shape'][1]

# Basic tokenizer: ASCII character to int ID (you can customize this)
def tokenize(text, max_len):
    token_ids = [ord(c) for c in text.lower()[:max_len]]
    token_ids += [0] * (max_len - len(token_ids))
    return np.array([token_ids], dtype=input_details[0]['dtype'])

# Run inference
input_data = tokenize(sample_text, input_len)
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])

print("✅ Inference result for input:", sample_text)
print(output_data)
