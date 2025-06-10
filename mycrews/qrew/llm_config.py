# mycrews/qrew/llm_config.py
from crewai import LLM
# from crewai.llms.ollama import OllamaLLM # Alternative if specific class is preferred

# Attempt to initialize the Ollama LLM
# Users should have Ollama running and a model like 'openhermes' pulled.
try:
    # Using the generic LLM class as per current main CrewAI LLM docs
    # Replace 'openhermes' with the desired default Ollama model for the project
    # Ensure Ollama server is running at http://localhost:11434
    default_llm = LLM(
        model="ollama/openhermes",
        base_url="http://localhost:11434"
    )

    # Alternatively, if using the specific OllamaLLM class:
    # from crewai.llms.ollama import OllamaLLM
    # default_llm = OllamaLLM(model="openhermes")
    # Note: OllamaLLM might have different default for base_url or expect it from env.
    # The generic 'LLM' class with 'ollama/' prefix and base_url is safer per docs.

    print("Successfully initialized Ollama LLM in llm_config.py.")
except Exception as e:
    print(f"Failed to initialize Ollama LLM in llm_config.py: {e}")
    print("Please ensure Ollama is running and the model (e.g., 'openhermes') is available.")
    print("Falling back to no default LLM. Agents will need LLM explicitly assigned or rely on global env vars.")
    default_llm = None
