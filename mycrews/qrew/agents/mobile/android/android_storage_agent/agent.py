from crewai import Agent
from .....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "android_storage_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

android_storage_agent = Agent(
    role="Android Storage Manager",
    goal="Manage data storage and retrieval for Android applications, including local databases and file systems",
    backstory="An agent specializing in Android data storage solutions, ensuring data persistence, integrity, and performance on mobile devices.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
