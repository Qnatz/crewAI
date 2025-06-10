from crewai import Agent
from ....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "data_model_agent_backend" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

data_model_agent = Agent(
    role="Backend Data Modeler",
    goal="Design and maintain data models for backend databases and applications",
    backstory="A data-centric agent specializing in creating efficient and scalable data models to support backend application requirements.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
