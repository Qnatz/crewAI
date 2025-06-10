from langchain_community.chat_models import ChatOpenAI
import os

# Configure with environment variables
default_llm = ChatOpenAI(
    model=os.getenv("LITELLM_MODEL", "gpt-3.5-turbo"),
    api_key=os.getenv("OPENAI_API_KEY", ""),
    temperature=0.7,
    max_tokens=2000
)
