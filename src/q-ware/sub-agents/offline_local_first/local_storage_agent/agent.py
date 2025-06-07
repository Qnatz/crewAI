from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

local_storage_agent = Agent(
    role="Local Storage Agent",
    goal="Abstract local DB (IndexedDB, SQLite) for web & mobile.",
    backstory="Specializes in managing local data storage across different platforms (web and mobile), providing a consistent interface for IndexedDB, SQLite, or other local database solutions.",
    tools=my_tools,
    allow_delegation=False,
    # llm=llm,
    verbose=True
)
