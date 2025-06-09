import numpy as np
print("Attempting to import tflite_runtime.interpreter...")
try:
    from tflite_runtime.interpreter import Interpreter
    print("tflite_runtime.interpreter.Interpreter imported successfully.")

    # Optional: Try to instantiate it with a dummy path to see if that part works
    # This is similar to how tools/embedder.py handles it initially.
    try:
        dummy_interpreter = Interpreter(model_path="dummy_non_existent_model.tflite")
        # This is expected to fail with a ValueError if the model file doesn't exist,
        # but it means the Interpreter class itself loaded and tried to work.
    except ValueError as ve:
        if "Could not open" in str(ve) or "No such file or directory" in str(ve) or "Failed to load model" in str(ve):
            print(f"Interpreter class instantiated but failed to load dummy model as expected: {ve}")
        else:
            raise # Re-raise if it's an unexpected ValueError
    except Exception as e:
        print(f"Error during Interpreter instantiation with dummy path: {e}")
        exit(1)

    print("TFLite runtime basic import and instantiation test passed.")

except ImportError as ie:
    print(f"Failed to import from tflite_runtime: {ie}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)
