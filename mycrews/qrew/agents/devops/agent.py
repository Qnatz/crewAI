from crewai import Agent
from ...llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "devops_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

devops_agent = Agent(
    role="DevOps Engineer",
    goal="Automate and streamline software development and deployment processes",
    backstory="An experienced DevOps professional focused on building and maintaining CI/CD pipelines, managing infrastructure, and ensuring system reliability.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
