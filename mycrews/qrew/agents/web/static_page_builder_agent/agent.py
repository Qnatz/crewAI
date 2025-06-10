from crewai import Agent
from ....llm_config import get_llm_for_agent

# Use the agent's role or a unique key for the lookup
agent_identifier = "static_page_builder_agent_web" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

static_page_builder_agent = Agent(
    role="Static Web Page Builder",
    goal="Develop and maintain static web pages using HTML, CSS, and JavaScript",
    backstory="A web developer focused on creating fast, secure, and reliable static websites.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
