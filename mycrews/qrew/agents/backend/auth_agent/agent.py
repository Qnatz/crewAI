from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools import FileSystemTool, ShellTool, DatabaseTool # Assuming this path

# Instantiate tools
file_system_tool = FileSystemTool()
shell_tool = ShellTool()
database_tool = DatabaseTool()

# Use the agent's role or a unique key for the lookup
agent_identifier = "auth_agent_backend" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

auth_agent = Agent(
    role="Backend Authentication Agent",
    goal="Implement and manage authentication and authorization logic for backend services",
    backstory="A security-focused agent responsible for safeguarding backend systems by implementing and enforcing authentication and authorization policies.",
    llm=specific_llm, # Assign the fetched LLM
    tools=[file_system_tool, shell_tool, database_tool], # Added tools
    allow_delegation=False,
    verbose=True
)
