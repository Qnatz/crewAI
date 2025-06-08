from crewai import Agent
from q_ware.llm_config import get_llm

# Placeholder for importing sub-agents that will be delegated to.
# Example:
# from src.q_ware.sub_agents.backend.auth_agent import auth_agent
# from src.q_ware.sub_agents.backend.data_model_agent import data_model_agent
# from src.q_ware.sub_agents.backend.api_creator_agent import api_creator_agent
# from src.q_ware.sub_agents.backend.sync_agent import sync_agent
# from src.q_ware.sub_agents.dev_utilities.debugger_agent import debugger_agent
# from src.q_ware.sub_agents.dev_utilities.tester_agent import tester_agent

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
backend_project_coordinator_agent = Agent(
    role="Backend Project Coordinator",
    goal="Decide DB and auth stack, manage model/API creation order, handle offline sync if flagged, and run debug/test pipeline for backend projects.",
    backstory="This lead agent orchestrates backend development. It determines the appropriate database and authentication stack, sequences the creation of data models and APIs, manages offline synchronization logic by delegating to SyncAgent, and oversees the debugging and testing pipeline through DebuggerAgent and TesterAgent.",
    allow_delegation=True,
    llm=llm,
    verbose=True
)
