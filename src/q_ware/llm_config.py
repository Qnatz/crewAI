import os
# from crewai.llms import ChatGoogleGenerativeAI # Ideal if CrewAI has a direct wrapper
# Or from langchain_google_vertexai import ChatVertexAI # If using Vertex AI
# Or from langchain_community.chat_models import ChatGoogleGenerativeAI # If using Google AI SDK via Langchain community
# For this placeholder, we'll just simulate the structure.
# Replace 'PlaceholderGeminiLLM' with the actual class and import.

# class PlaceholderGeminiLLM:
#     """
#     This is a placeholder for the actual Gemini LLM client.
#     Replace this with the actual library import and instantiation, e.g.:
#     from langchain_google_vertexai import ChatVertexAI
#     llm = ChatVertexAI(model_name=model_name, project="your-gcp-project")
#     or from crewai.llms import ChatGoogleGenerativeAI (if available)
#     llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
#     """
#     def __init__(self, model_name: str, api_key: str = None):
#         self.model_name = model_name
#         self.api_key = api_key
#         if not api_key:
#             print(f"Warning: PlaceholderGeminiLLM for '{model_name}' initialized without a specific API key. "
#                   "Ensure the environment is configured for default authentication if this is intentional for the actual library.")
#         print(f"PlaceholderGeminiLLM initialized with model: {self.model_name}")

#     def __repr__(self):
#         return f"PlaceholderGeminiLLM(model_name='{self.model_name}')"

# Global LLM instance to be reused by agents
# This helps in making only one LLM object for the application if configuration doesn't change.
_llm_instance = None

from crewai import LLM # Changed import

def get_llm():
    """
    Retrieves an initialized LLM instance, configured for Gemini
    based on environment variables.
    """
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-latest") # Default model

    if not api_key:
        # Depending on the actual Gemini library, API key might be optional if other auth methods are set up (e.g. gcloud CLI, service accounts)
        # For now, we'll print a strong warning if it's missing, as many direct API uses require it.
        print("Warning: GEMINI_API_KEY environment variable not found. "
              "The application might not be able to connect to the Gemini LLM.")
        # Decide if you want to raise an error or allow it to proceed (some libs might use default auth)
        # raise ValueError("GEMINI_API_KEY not found in environment variables.")

    # Replace PlaceholderGeminiLLM with the actual Gemini LLM client instantiation
    # Example using a hypothetical CrewAI wrapper (ideal):
    # from crewai.llms import ChatGoogleGenerativeAI
    # _llm_instance = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
    #
    # Example using Langchain via Vertex AI (if you have a GCP project and Vertex AI enabled):
    # from langchain_google_vertexai import ChatVertexAI
    # project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    # if not project_id:
    #     print("Warning: GOOGLE_CLOUD_PROJECT environment variable not set for Vertex AI.")
    # _llm_instance = ChatVertexAI(model_name=model_name, project=project_id) # API key often handled by gcloud auth
    #
    # For now, using the placeholder:
    # _llm_instance = PlaceholderGeminiLLM(model_name=model_name, api_key=api_key)
    _llm_instance = LLM( # Changed to LLM
        model=model_name,
        api_key=api_key # TODO: Replace with your actual Gemini API key or ensure GEMINI_API_KEY env var is set.
        # base_url="https://generativelanguage.googleapis.com/v1beta" # Removed base_url
    )

    print(f"LLM instance created/retrieved: {_llm_instance}")
    return _llm_instance

# To test this module directly (optional)
if __name__ == '__main__':
    # Create a dummy .env file for testing this script
    # In a real scenario, this would be your actual .env file
    print("Testing llm_config.py...")
    if not os.path.exists(".env"):
        with open(".env_temp_test", "w") as f:
            f.write('GEMINI_API_KEY="test_key_123"\n')
            f.write('GEMINI_MODEL_NAME="gemini-1.0-pro"\n') # Example different model
        # Temporarily set an env variable to load this if .env doesn't exist
        # This is just for the __main__ block test, real app uses load_dotenv() in main.py
        os.environ["PYTHON_DOTENV_PATH"] = ".env_temp_test"
        from dotenv import load_dotenv # Requires python-dotenv to be installed
        did_load = load_dotenv()
        print(f"Loaded .env_temp_test: {did_load}")


    llm = get_llm()
    print(f"Retrieved LLM: {llm}")
    print(f"Model: {llm.model_name if hasattr(llm, 'model_name') else 'N/A'}")

    # Test memoization
    llm2 = get_llm()
    print(f"Retrieved LLM again: {llm2}")
    print(f"Is same instance: {llm is llm2}")

    if os.path.exists(".env_temp_test"):
        os.remove(".env_temp_test")
        if "PYTHON_DOTENV_PATH" in os.environ:
            del os.environ["PYTHON_DOTENV_PATH"]
