from crewai import Agent
from ....llm_config import get_llm_for_agent # Adjusted path
from ....tools import APICallTool, DatabaseTool, FileSystemTool, ShellTool

# Instantiate tools
api_call_tool = APICallTool()
database_tool = DatabaseTool()
file_system_tool = FileSystemTool()
shell_tool = ShellTool()

# Use the agent's role or a unique key for the lookup
agent_identifier = "auth_coordinator_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

auth_coordinator_agent = Agent(
    role="Authentication Coordinator",
    goal="Manage user authentication and authorization processes",
    backstory="An experienced agent responsible for overseeing all aspects of user authentication and authorization, ensuring secure and efficient access control.",
    llm=specific_llm, # Assign the fetched LLM
    tools=[api_call_tool, database_tool, file_system_tool, shell_tool], # Added tools
    allow_delegation=False, # Note: allow_delegation is False, but a coordinator might often delegate. This might be reviewed.
    verbose=True
)
