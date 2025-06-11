from crewai import Agent
from ...llm_config import get_llm_for_agent
from ...tools.custom_agent_tools import CustomDelegateWorkTool, CustomAskQuestionTool
# from crewAI.qrew.tools.file_io_tool import FileIOTool # Example if tools are ready

# Use the agent's role or a unique key for the lookup
agent_identifier = "project_architect_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

# Instantiate custom tools
custom_delegate_tool = CustomDelegateWorkTool()
custom_ask_question_tool = CustomAskQuestionTool()

# Example: If FileIOTool or other tools are also needed by this agent
# from ....tools.file_io_tool import FileIOTool # Make sure this path is correct if used
# file_io_tool = FileIOTool()
# agent_tools = [custom_delegate_tool, custom_ask_question_tool, file_io_tool]

agent_tools = [] # Removed custom_delegate_tool and custom_ask_question_tool

project_architect_agent = Agent(
    role="Project Architect",
    goal="Design a robust and scalable software architecture based on project requirements, constraints, and technical vision, "
         "all detailed in the task description. Ensure the architecture aligns with best practices.",
    backstory="A seasoned software architect with extensive experience in designing complex systems across various domains. "
              "Known for creating elegant, maintainable, and future-proof architectures. "
              "Possesses deep knowledge of design patterns, system integration, and technology stacks.",
    llm=specific_llm, # Assign the fetched LLM
    # tools=agent_tools, # Removed as agent_tools is now empty
    allow_delegation=True, # This will be used by defining sub-tasks, not by the agent itself using a tool.
    verbose=True
)
