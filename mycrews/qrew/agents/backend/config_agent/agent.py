from crewai import Agent
from ....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "config_agent_backend" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

config_agent = Agent(
    role="Backend Configuration Manager",
    goal="Manage and maintain configuration settings for backend applications and services",
    backstory="An organized agent dedicated to ensuring backend systems are correctly configured for optimal performance, security, and reliability.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
