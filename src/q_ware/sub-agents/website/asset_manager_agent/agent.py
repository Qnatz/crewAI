from crewai import Agent
from .tools import my_tools
# No get_llm import needed as we are hardcoding the string directly from crewai.agent default
# from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

asset_manager_agent = Agent(
    role="Asset Manager",
    goal="Optimize images, inject SEO/meta tags, manage media assets.",
    backstory="A specialist in web asset optimization and management, ensuring images are compressed, SEO tags are correctly implemented, and all media assets are efficiently handled.",
    tools=my_tools,
    allow_delegation=False,
    llm="gemini/gemini-1.5-pro-latest", # Uncomment and configure if an LLM is to be used
    verbose=True
)
