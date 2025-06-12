from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools import FileSystemTool, ShellTool, save_code # Added import

# Instantiate tools
file_system_tool = FileSystemTool() # Added instantiation
shell_tool = ShellTool() # Added instantiation
# save_code is a function, so it's used directly

# Use the agent's role or a unique key for the lookup
agent_identifier = "static_page_builder_agent_web"
specific_llm = get_llm_for_agent(agent_identifier)

static_page_builder_agent = Agent(
    role="Static Web Page Builder",
    goal="Develop and maintain static web pages using HTML, CSS, and JavaScript",
    backstory="A web developer focused on creating fast, secure, and reliable static websites.",
    llm=specific_llm,
    tools=[file_system_tool, shell_tool, save_code], # Added tools list
    allow_delegation=False,
    verbose=True
)
