import os
# from crewai.utilities.config import Config, llm_config # type: ignore # This seems to be an outdated import
from langchain_community.llms import Ollama # Default if not LiteLLM
from langchain_community.chat_models.litellm import ChatLiteLLM # type: ignore

# Default LLM configuration (e.g., Ollama)
# This will be used if no specific API keys or models are configured via environment variables.
default_llm = Ollama(model=os.environ.get("OLLAMA_MODEL", "openhermes"))
configured_llm = None

try:
    # Ensure litellm is installed. If not, this will raise an ImportError.
    # The user is responsible for installing litellm: pip install litellm
    import litellm # type: ignore

    # Determine which LLM to configure based on environment variables
    LITELLM_MODEL = os.environ.get("LITELLM_MODEL")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    # Add other API key checks as needed (e.g., COHERE_API_KEY)

    if LITELLM_MODEL:
        print(f"LITELLM_MODEL environment variable found: {LITELLM_MODEL}")
        # Check for OpenAI models (e.g., "gpt-4", "openai/gpt-3.5-turbo")
        if "gpt-" in LITELLM_MODEL.lower() or "openai/" in LITELLM_MODEL.lower() or LITELLM_MODEL.lower().startswith("text-davinci"):
            if OPENAI_API_KEY:
                print(f"Found OPENAI_API_KEY, configuring LiteLLM with OpenAI model: {LITELLM_MODEL}")
                # LiteLLM will automatically pick up OPENAI_API_KEY from the environment.
                configured_llm = ChatLiteLLM(model=LITELLM_MODEL)
            else:
                print(f"LITELLM_MODEL is set to '{LITELLM_MODEL}' which appears to be an OpenAI model, but OPENAI_API_KEY is not found in the environment.")
                print("Please set the OPENAI_API_KEY environment variable.")
        # Check for Gemini models (e.g., "gemini/gemini-1.5-flash", "gemini-pro")
        elif "gemini" in LITELLM_MODEL.lower():
            if GEMINI_API_KEY:
                print(f"Found GEMINI_API_KEY, configuring LiteLLM with Gemini model: {LITELLM_MODEL}")
                # LiteLLM will automatically pick up GEMINI_API_KEY.
                # Ensure LITELLM_MODEL is prefixed with "gemini/" if required by LiteLLM, e.g., "gemini/gemini-1.5-flash"
                model_name = LITELLM_MODEL if "gemini/" in LITELLM_MODEL.lower() else f"gemini/{LITELLM_MODEL}"
                configured_llm = ChatLiteLLM(model=model_name)
                print(f"Using Gemini model: {model_name}")
            else:
                print(f"LITELLM_MODEL is set to '{LITELLM_MODEL}' which appears to be a Gemini model, but GEMINI_API_KEY is not found in the environment.")
                print("Please set the GEMINI_API_KEY environment variable.")
        # Check for Anthropic models (e.g., "claude-3-opus-20240229", "anthropic/claude-2")
        elif "claude" in LITELLM_MODEL.lower() or "anthropic/" in LITELLM_MODEL.lower():
            if ANTHROPIC_API_KEY:
                print(f"Found ANTHROPIC_API_KEY, configuring LiteLLM with Anthropic model: {LITELLM_MODEL}")
                # LiteLLM will automatically pick up ANTHROPIC_API_KEY.
                configured_llm = ChatLiteLLM(model=LITELLM_MODEL)
            else:
                print(f"LITELLM_MODEL is set to '{LITELLM_MODEL}' which appears to be an Anthropic model, but ANTHROPIC_API_KEY is not found in the environment.")
                print("Please set the ANTHROPIC_API_KEY environment variable.")
        else:
            # For other models specified by LITELLM_MODEL, assume the necessary API key (if any) is globally available
            # or the model runs locally (like some Ollama models via LiteLLM).
            # Check if a known API key is present that might correspond to the model type.
            api_key_present = OPENAI_API_KEY or GEMINI_API_KEY or ANTHROPIC_API_KEY # Add other keys if needed
            if not api_key_present and not ("ollama" in LITELLM_MODEL.lower() or "local" in LITELLM_MODEL.lower()): # Basic check for local model
                 print(f"LITELLM_MODEL is '{LITELLM_MODEL}'. Ensure any required API keys (e.g., OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY) are set if this is a hosted model.")
            else:
                print(f"Configuring LiteLLM with model: {LITELLM_MODEL}. Trusting API key is set if required and not explicitly checked above.")
            configured_llm = ChatLiteLLM(model=LITELLM_MODEL)

    elif GEMINI_API_KEY: # If LITELLM_MODEL is not set, but GEMINI_API_KEY is, default to a Gemini model
        print("GEMINI_API_KEY found, LITELLM_MODEL not set. Defaulting to 'gemini/gemini-1.5-flash'.")
        # Ensure you have a default gemini model name or make it configurable
        default_gemini_model = "gemini/gemini-1.5-flash"
        configured_llm = ChatLiteLLM(model=default_gemini_model)
    elif OPENAI_API_KEY: # If LITELLM_MODEL is not set, but OPENAI_API_KEY is, default to an OpenAI model
        print("OPENAI_API_KEY found, LITELLM_MODEL not set. Defaulting to 'gpt-3.5-turbo'.")
        default_openai_model = "gpt-3.5-turbo"
        configured_llm = ChatLiteLLM(model=default_openai_model)
    # Add other provider defaults here if LITELLM_MODEL is not set but their key is present
    # E.g., elif ANTHROPIC_API_KEY: ...

    if not configured_llm:
        print("No specific API keys (GEMINI_API_KEY, OPENAI_API_KEY, etc.) or LITELLM_MODEL directing to a hosted model were found.")
        print(f"Falling back to default LLM: {default_llm.model if hasattr(default_llm, 'model') else 'Ollama'}")
        configured_llm = default_llm

except ImportError:
    print("LiteLLM is not installed. Please install it using 'pip install litellm'.")
    print(f"Falling back to default LLM: {default_llm.model if hasattr(default_llm, 'model') else 'Ollama'}")
    configured_llm = default_llm
except Exception as e:
    print(f"An error occurred during LiteLLM configuration: {e}")
    print(f"Falling back to default LLM: {default_llm.model if hasattr(default_llm, 'model') else 'Ollama'}")
    configured_llm = default_llm


# Set the chosen LLM in CrewAI config
# This makes it the default for all agents unless overridden.
# llm_config.set(configured_llm) # The llm_config object is not available from the import above.
                                # Global LLM configuration might need a different approach in this crewai version.

# You can also store other configurations here
# For example, a default embedding model if needed by multiple agents
# from langchain_community.embeddings import OllamaEmbeddings # type: ignore
# embedding_model = OllamaEmbeddings(model="nomic-embed-text")
# Config.set_embedding_model(embedding_model) # Example

print(f"CrewAI global LLM set to: {configured_llm.model if hasattr(configured_llm, 'model') else str(configured_llm)}")
if hasattr(configured_llm, 'model_name') and configured_llm.model_name: # For Langchain objects that have model_name
    print(f"Model name from llm_config: {configured_llm.model_name}")


# To verify, you can try:
# from crewai import Agent
# agent = Agent(role="test", goal="test", backstory="test") # This will use the default LLM
# print(agent.llm.invoke("Hello"))
