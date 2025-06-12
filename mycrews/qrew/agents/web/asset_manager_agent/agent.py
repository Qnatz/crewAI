from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools import FileSystemTool, ShellTool # Added import

# Instantiate tools
file_system_tool = FileSystemTool() # Added instantiation
shell_tool = ShellTool() # Added instantiation

# Use the agent's role or a unique key for the lookup
agent_identifier = "asset_manager_agent_web"
specific_llm = get_llm_for_agent(agent_identifier)

asset_manager_agent = Agent(
    role="Web Asset Manager",
    goal="Manage and optimize static assets (images, CSS, JavaScript) for web applications",
    backstory="An agent focused on efficient asset management, ensuring fast loading times and optimal performance for web applications.",
    llm=specific_llm,
    tools=[file_system_tool, shell_tool], # Added tools list
    allow_delegation=False,
    verbose=True
)
