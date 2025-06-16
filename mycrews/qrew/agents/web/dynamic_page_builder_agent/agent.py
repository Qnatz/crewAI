from crewai import Agent
from ....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "dynamic_page_builder_agent_web" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

dynamic_page_builder_agent = Agent(
    role="Dynamic Web Page Builder",
    goal="Develop and maintain dynamic web pages and user interfaces using server-side and client-side technologies",
    backstory="A skilled web developer specializing in creating interactive and data-driven web pages that provide engaging user experiences.",
    llm=specific_llm, # Assign the fetched LLM
    type="web",
    allow_delegation=False,
    verbose=True
)
