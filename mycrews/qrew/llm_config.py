# mycrews/qrew/llm_config.py
import os
from crewai import LLM

# Initialize LLM variables to None
llm_gemini_1_5_flash = None
llm_gemini_2_0_flash = None
default_llm = None

# Get GEMINI_API_KEY from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    print("GEMINI_API_KEY found. Attempting to initialize Gemini LLMs...")

    # Instantiate gemini-1.5-flash
    try:
        llm_gemini_1_5_flash = LLM(model="gemini/gemini-1.5-flash")
        # Note: For Gemini, crewai's LLM class typically expects the API key
        # to be picked up automatically from the environment by the underlying provider (e.g., LiteLLM or LangChain).
        # If crewai's generic LLM class doesn't directly support Gemini without further config,
        # this might require crewai.llms.gemini.GeminiLLM or similar, or ensuring LiteLLM is configured for Gemini.
        # For this task, we assume crewai.LLM can handle "gemini/model-name" if the key is in env.
        print("Successfully attempted to initialize llm_gemini_1_5_flash.")
    except Exception as e:
        print(f"Failed to initialize llm_gemini_1_5_flash: {e}")
        llm_gemini_1_5_flash = None

    # Instantiate gemini-2.0-flash-001 (assuming this is a valid model identifier for the provider)
    # Note: Model names for upcoming versions like "2.0" might be speculative or internal.
    # Using a placeholder name as per request.
    try:
        llm_gemini_2_0_flash = LLM(model="gemini/gemini-2.0-flash-001")
        print("Successfully attempted to initialize llm_gemini_2_0_flash.")
    except Exception as e:
        print(f"Failed to initialize llm_gemini_2_0_flash: {e}")
        llm_gemini_2_0_flash = None

    # Set default_llm
    default_llm = llm_gemini_1_5_flash
    if default_llm:
        print(f"Default LLM set to gemini-1.5-flash.")
    else:
        print("Default LLM (gemini-1.5-flash) could not be initialized.")

else:
    print("GEMINI_API_KEY not found in environment variables.")
    print("Gemini LLMs (gemini-1.5-flash, gemini-2.0-flash-001) will not be initialized.")
    print("default_llm will be None. Agents will need LLM explicitly assigned or rely on other fallbacks.")

if default_llm is None:
    print("llm_config.py: default_llm is None. The application might not have a default LLM configured.")
