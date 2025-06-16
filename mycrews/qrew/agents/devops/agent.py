from crewai import Agent
from ...llm_config import get_llm_for_agent
from ...tools.knowledge_base_tool import knowledge_base_tool_instance

# Use the agent's role or a unique key for the lookup
agent_identifier = "devops_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

devops_agent = Agent(
    role="DevOps Engineer",
    goal="Automate and streamline software development and deployment processes",
    backstory="An experienced DevOps professional focused on building and maintaining CI/CD pipelines, managing infrastructure, and ensuring system reliability.",
    llm=specific_llm, # Assign the fetched LLM
    tools=[knowledge_base_tool_instance], # Added KnowledgeBaseTool instance
    type="devops",
    allow_delegation=False,
    verbose=True
)
