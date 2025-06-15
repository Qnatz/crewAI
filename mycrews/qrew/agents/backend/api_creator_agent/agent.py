from crewai import Agent
from ....llm_config import get_llm_for_agent
from ....tools.knowledge_base_tool import knowledge_base_tool_instance

# Use the agent's role or a unique key for the lookup
agent_identifier = "api_creator_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

api_creator_agent = Agent(
    role="Backend API Creator",
    goal="Design, develop, and maintain robust and scalable backend APIs",
    backstory="A skilled backend developer specializing in API creation, ensuring seamless data exchange and application functionality.",
    llm=specific_llm, # Assign the fetched LLM
    tools=[knowledge_base_tool_instance], # Added KnowledgeBaseTool instance
    allow_delegation=False,
    verbose=True
)
