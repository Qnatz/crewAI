from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools.knowledge_base_tool import knowledge_base_tool_instance

# Use the agent's role or a unique key for the lookup
agent_identifier = "tester_agent_devutils" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

tester_agent = Agent(
    role="Software Tester",
    goal="Design, implement, and execute tests to ensure software quality and reliability",
    backstory="A dedicated quality assurance professional committed to identifying and reporting software defects through rigorous testing.",
    llm=specific_llm, # Assign the fetched LLM
    tools=[knowledge_base_tool_instance], # Added KnowledgeBaseTool instance
    allow_delegation=False,
    verbose=True
)
