import os
from crewai.config import Config, llm_config
from langchain_community.llms import Ollama # Default if not LiteLLM
from langchain_community.chat_models.litellm import ChatLiteLLM

# Check for a specific environment variable to enable LiteLLM, otherwise default or error
# For this setup, we'll prioritize LiteLLM with Gemini if the API key is available.

# Attempt to load Gemini API key from environment
gemini_api_key = os.environ.get("GEMINI_API_KEY")

# Default LLM configuration (can be any LangChain LLM)
# For example, using Ollama if LiteLLM/Gemini is not configured
default_llm = Ollama(model="openhermes") # A common default if no API keys

# Configure LiteLLM for Gemini
# User wants to use 'gemini-1.5-flash'
# LiteLLM will automatically pick up GEMINI_API_KEY from the environment if set.
# See LiteLLM docs for more specific provider configurations if needed.
try:
    # Ensure litellm is installed. If not, this will raise an ImportError.
    # The user is responsible for installing litellm: pip install litellm
    import litellm

    # We will set the model and API key directly if the environment variable is present.
    # LiteLLM can also be configured globally using `litellm.set_verbose=True` or other settings.
    # For CrewAI, we typically wrap LiteLLM with `ChatLiteLLM` or use a custom wrapper.

    # Option 1: Basic ChatLiteLLM from LangChain Community (recommended for CrewAI)
    # This uses litellm.completion under the hood.
    # GEMINI_API_KEY should be automatically picked up by litellm if set in the environment.
    # For specific providers like Gemini, sometimes you might need to prefix the model name,
    # e.g., "gemini/gemini-1.5-flash" - check LiteLLM documentation for Gemini specifics.
    # For this example, we assume "gemini-1.5-flash" is directly supported or GEMINI_API_KEY handles routing.

    # Let's define a default model name, can be overridden by env var too
    LITELLM_MODEL = os.environ.get("LITELLM_MODEL", "gemini/gemini-1.5-flash")
                                    # Using "gemini/" prefix as is common for some providers in LiteLLM

    # Initialize ChatLiteLLM
    # Note: Actual API key handling for Gemini with LiteLLM might require
    # setting os.environ["GEMINI_API_KEY"] = "your_key" before this call,
    # or specific provider params in ChatLiteLLM if supported.
    # We assume GEMINI_API_KEY is set in the environment where this code runs.

    # If gemini_api_key is explicitly found, we can be more confident.
    if gemini_api_key:
        print(f"Found GEMINI_API_KEY, configuring LiteLLM with model: {LITELLM_MODEL}")
        # Some LiteLLM configurations might require passing the api_key directly if not globally set
        # For ChatLiteLLM, it often relies on litellm's global config or direct env var usage by litellm.completion
        # If issues occur, one might need to do: litellm.api_key = gemini_api_key (but this is global)
        # Or specific provider setup if ChatLiteLLM allows, e.g. model_kwargs={"api_key": gemini_api_key} if that were an option.
        # For now, relying on litellm's auto-detection of GEMINI_API_KEY.
        configured_llm = ChatLiteLLM(model=LITELLM_MODEL)
    else:
        print("GEMINI_API_KEY not found in environment. LiteLLM for Gemini might not work.")
        print(f"Falling back to default LLM: {default_llm.model if hasattr(default_llm, 'model') else 'Ollama'}")
        configured_llm = default_llm

except ImportError:
    print("LiteLLM is not installed. Please install it using 'pip install litellm'.")
    print(f"Falling back to default LLM: {default_llm.model if hasattr(default_llm, 'model') else 'Ollama'}")
    configured_llm = default_llm
except Exception as e:
    print(f"Error configuring LiteLLM: {e}")
    print(f"Falling back to default LLM: {default_llm.model if hasattr(default_llm, 'model') else 'Ollama'}")
    configured_llm = default_llm


# Set the chosen LLM in CrewAI config
# This makes it the default for all agents unless overridden.
llm_config.set(configured_llm)

# You can also store other configurations here
# For example, a default embedding model if needed by multiple agents
# from langchain_community.embeddings import OllamaEmbeddings
# embedding_model = OllamaEmbeddings(model="nomic-embed-text")
# Config.set_embedding_model(embedding_model) # Example

print(f"CrewAI global LLM set to: {llm_config.get().model_name if hasattr(llm_config.get(), 'model_name') else str(llm_config.get())}")

# To verify, you can try:
# from crewai import Agent
# agent = Agent(role="test", goal="test", backstory="test") # This will use the default LLM
# print(agent.llm.invoke("Hello"))
