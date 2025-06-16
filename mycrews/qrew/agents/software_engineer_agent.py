from crewai import Agent
from ..llm_config import get_llm_for_agent # Adjusted import path
from mycrews.qrew.tools.knowledge_base_tool import KnowledgeBaseTool

# Use the agent's role or a unique key for the lookup
agent_identifier = "software_engineer_agent"
specific_llm = get_llm_for_agent(agent_identifier)

software_engineer_agent = Agent(
    role="Software Engineer",
    goal="To meticulously design, develop, and implement software components and systems based on detailed architectural plans and technical specifications. "
         "This includes creating database schemas, defining API contracts, structuring UI components, and writing robust code.",
    backstory="A versatile and highly skilled software engineer with a broad understanding of different technologies and programming paradigms. "
              "Adept at translating architectural blueprints into functional and efficient code, with a strong focus on quality, maintainability, and scalability. "
              "Comfortable working across the full stack and on various aspects of software development, from backend logic to frontend interfaces."
              " This engineer actively consults the project's knowledge base to ensure consistency with existing architectures, to reuse established patterns, and to leverage proven utility functions and API schemas, thereby enhancing the quality and efficiency of the development process.",
    llm=specific_llm,
    tools=[KnowledgeBaseTool()], # Initialize with empty knowledge_sources
    knowledge_sources=[], # Added as per instruction
    allow_delegation=False, # This agent executes tasks, does not delegate them further
    verbose=True
)

# To allow easy import of the agent
# from mycrews.qrew.agents.software_engineer_agent import software_engineer_agent
