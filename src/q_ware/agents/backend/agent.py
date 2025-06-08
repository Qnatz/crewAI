from crewai import Agent
# Import sub-agents - paths need to be relative to the q_ware root or use full paths
from q_ware.agents.backend.auth_agent import auth_agent
from q_ware.agents.backend.api_creator_agent import api_creator_agent
from q_ware.agents.backend.data_model_agent import data_model_agent
from q_ware.agents.backend.config_agent import config_agent
from q_ware.agents.backend.storage_agent import storage_agent
from q_ware.agents.backend.queue_agent import queue_agent
from q_ware.agents.backend.sync_agent import sync_agent
from .tools import my_tools # Tools specific to the coordinator

backend_coordinator_agent = Agent(
    role="Backend Coordination Agent",
    goal="Orchestrate all backend-related subagents by delegating tasks and ensuring integration between them.",
    backstory=(
        "You are a backend coordination agent. Your goal is to orchestrate all backend-related subagents "
        "by delegating tasks and ensuring integration between them.\n\n"
        "Responsibilities:\n"
        "- Decompose backend requirements into specific tasks\n"
        "- Assign each task to a subagent with the required context\n"
        "- Maintain architectural integrity and enforce shared backend patterns\n"
        "- Monitor progress and validate outputs from each subagent\n"
        "- Report completion, blockers, or escalations to higher-level agents\n\n"
        "Available Subagents:\n"
        "- auth_agent\n"
        "- api_creator_agent\n"
        "- data_model_agent\n"
        "- config_agent\n"
        "- storage_agent\n"
        "- queue_agent\n"
        "- sync_agent\n\n"
        "Input:\n"
        "You will receive a JSON backend feature specification from a top-level agent.\n\n"
        "Output:\n"
        "- Subagent task queue\n"
        "- Integration plan\n"
        "- Status report"
    ),
    tools=my_tools, # Add any tools the coordinator itself might use (e.g., for planning, code analysis)
    # List of agents that can be delegated to.
    # CrewAI typically discovers agents available in its Crew context for delegation.
    # Explicitly listing them here might be for documentation or specific routing if not using a Crew.
    # However, the primary mechanism for delegation is through Tasks assigned to specific agents within a Crew.
    # For now, we'll rely on the Crew definition to manage agent availability for delegation.
    # agents=[
    #     auth_agent,
    #     api_creator_agent,
    #     data_model_agent,
    #     config_agent,
    #     storage_agent,
    #     queue_agent,
    #     sync_agent
    # ],
    allow_delegation=True,
    verbose=True,
    llm="gemini/gemini-1.5-pro-latest"
)
