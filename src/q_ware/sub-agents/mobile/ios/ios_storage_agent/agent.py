from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
ios_storage_agent = Agent(
    role="iOS Storage Agent",
    goal="Set up CoreData schemas and model objects.",
    backstory="Responsible for local data persistence on iOS devices. Sets up CoreData schemas and manages model objects for efficient data storage and retrieval.",
    tools=my_tools,
    allow_delegation=False,
    llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
