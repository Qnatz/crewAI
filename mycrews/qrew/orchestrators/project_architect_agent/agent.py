from crewai import Agent
from ...llm_config import get_llm_for_agent
# from crewAI.qrew.tools.file_io_tool import FileIOTool # Example if tools are ready

# Use the agent's role or a unique key for the lookup
agent_identifier = "project_architect_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

project_architect_agent = Agent(
    role="Project Architect",
    goal="Design a robust and scalable software architecture based on project requirements and constraints. "
         "Ensure the architecture aligns with best practices and technical vision. "
         "Input: {project_requirements}, {constraints}, {technical_vision}.",
    backstory="A seasoned software architect with extensive experience in designing complex systems across various domains. "
              "Known for creating elegant, maintainable, and future-proof architectures. "
              "Possesses deep knowledge of design patterns, system integration, and technology stacks.",
    llm=specific_llm, # Assign the fetched LLM
    # tools=[FileIOTool.read_file, FileIOTool.write_file], # Example: if FileIOTool is available and has these methods
    allow_delegation=True, # May delegate detailed design of specific components
    verbose=True
)
