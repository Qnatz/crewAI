from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
sync_agent = Agent(
    role="Backend Sync Agent",
    goal="Offline-first sync logic, conflict resolution between client & server.",
    backstory="This agent manages data synchronization between the client and server, with a focus on offline-first capabilities. It implements logic for handling data conflicts and ensuring eventual consistency.",
    tools=my_tools,
    allow_delegation=False,
    llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
