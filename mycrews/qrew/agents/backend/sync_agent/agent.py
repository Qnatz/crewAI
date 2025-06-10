from crewai import Agent
from ....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "sync_agent_backend" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

sync_agent = Agent(
    role="Backend Data Synchronizer",
    goal="Ensure data consistency and synchronization across multiple backend services and databases",
    backstory="An agent dedicated to maintaining data integrity by synchronizing data across distributed backend systems.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
