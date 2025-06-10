from crewai import Agent
from ....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "storage_agent_backend" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

storage_agent = Agent(
    role="Backend Storage Manager",
    goal="Manage data storage and retrieval for backend applications, including databases and file systems",
    backstory="An agent specializing in data storage solutions, ensuring data integrity, availability, and performance for backend systems.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
