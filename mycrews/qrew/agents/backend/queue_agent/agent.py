from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools import QueueManagementTool, FileSystemTool, ShellTool # Assuming this path

# Instantiate tools
queue_tool = QueueManagementTool()
file_system_tool = FileSystemTool()
shell_tool = ShellTool()

# Use the agent's role or a unique key for the lookup
agent_identifier = "queue_agent_backend" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

queue_agent = Agent(
    role="Backend Queue Manager",
    goal="Manage and process asynchronous tasks and message queues for backend services",
    backstory="An agent focused on ensuring reliable and efficient task processing by managing message queues and handling asynchronous operations in the backend.",
    llm=specific_llm, # Assign the fetched LLM
    tools=[queue_tool, file_system_tool, shell_tool], # Added tools
    allow_delegation=False,
    verbose=True
)
