from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools import FileSystemTool, ShellTool, APICallTool, save_code # Added import

# Instantiate tools
file_system_tool = FileSystemTool() # Added instantiation
shell_tool = ShellTool() # Added instantiation
api_call_tool = APICallTool() # Added instantiation
# save_code is a function, so it's used directly

# Use the agent's role or a unique key for the lookup
agent_identifier = "dynamic_page_builder_agent_web"
specific_llm = get_llm_for_agent(agent_identifier)

dynamic_page_builder_agent = Agent(
    role="Dynamic Web Page Builder",
    goal="Develop and maintain dynamic web pages and user interfaces using server-side and client-side technologies",
    backstory="A skilled web developer specializing in creating interactive and data-driven web pages that provide engaging user experiences.",
    llm=specific_llm,
    tools=[file_system_tool, shell_tool, api_call_tool, save_code], # Added tools list
    allow_delegation=False,
    verbose=True
)
