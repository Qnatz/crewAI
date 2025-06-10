from crewai import Agent
from ....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "code_writer_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

code_writer_agent = Agent(
    role="Code Writer",
    goal="Write clean, efficient, and well-documented code based on specifications",
    backstory="A proficient software developer with expertise in multiple programming languages, dedicated to producing high-quality code.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
