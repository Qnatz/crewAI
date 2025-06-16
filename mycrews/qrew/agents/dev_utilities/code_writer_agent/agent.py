from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools.knowledge_base_tool import knowledge_base_tool_instance

# Use the agent's role or a unique key for the lookup
agent_identifier = "code_writer_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

code_writer_agent = Agent(
    role="Code Writer",
    goal="Write clean, efficient, and well-documented code based on specifications",
    backstory="A proficient software developer with expertise in multiple programming languages, dedicated to producing high-quality code."
              " This developer actively consults the project's knowledge base for coding standards, reusable snippets, and established patterns to ensure consistency and accelerate development.",
    llm=specific_llm, # Assign the fetched LLM
    tools=[knowledge_base_tool_instance], # Added KnowledgeBaseTool instance
    knowledge_sources=[], # Added as per instruction
    allow_delegation=False,
    verbose=True
)
