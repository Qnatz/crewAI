from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools.knowledge_tools import file_reader_tool, directory_reader_tool
from ....tools.knowledge_base_tool import knowledge_base_tool_instance
from ....tools.custom_agent_tools import save_code

# Use the agent's role or a unique key for the lookup
agent_identifier = "logger_agent_devutils" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

logger_agent = Agent(
    role="Logger",
    goal="Implement and manage logging functionality for applications",
    backstory="An agent focused on ensuring comprehensive and effective logging to facilitate debugging, monitoring, and auditing.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True,
    tools=[file_reader_tool, save_code, knowledge_base_tool_instance, directory_reader_tool]
)
