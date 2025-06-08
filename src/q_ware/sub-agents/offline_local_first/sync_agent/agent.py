from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
sync_agent = Agent(
    role="Offline/Local-First Sync Agent",
    goal="Coordinate data reconciliation when reconnecting.",
    backstory="This SyncAgent is specialized for offline and local-first scenarios. It focuses on coordinating data reconciliation processes when a device or application reconnects to a network, ensuring data consistency between local storage and remote servers.",
    tools=my_tools,
    allow_delegation=False, # Usually a worker, but could delegate to specific conflict resolvers
    llm=llm,
    verbose=True
)
