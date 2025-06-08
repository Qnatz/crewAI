from crewai import Agent
from q_ware.llm_config import get_llm

# Placeholder for importing sub-agents that will be delegated to.
# Example:
# from src.q_ware.sub_agents.website.static_page_builder_agent import static_page_builder_agent
# from src.q_ware.sub_agents.website.dynamic_page_builder_agent import dynamic_page_builder_agent
# from src.q_ware.sub_agents.website.asset_manager_agent import asset_manager_agent
# from src.q_ware.sub_agents.backend.api_creator_agent import api_creator_agent
# from src.q_ware.sub_agents.dev_utilities.tester_agent import tester_agent
# from src.q_ware.sub_agents.dev_utilities.code_writer_agent import code_writer_agent

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview") # Or another appropriate model for coordination
llm = get_llm()
web_project_coordinator_agent = Agent(
    role="Web Project Coordinator",
    goal="Determine site type (static/dynamic), sequence asset preparation, page generation, and coordinate test coverage and final assembly for web projects.",
    backstory="A lead agent responsible for orchestrating web development projects. It intelligently delegates tasks to specialized sub-agents like StaticPageBuilder, DynamicPageBuilder, AssetManager, APICreator, Tester, and CodeWriter to ensure efficient project execution from asset preparation to final assembly and testing.",
    # tools=[], # Coordinator agents might not have tools directly
    allow_delegation=True, # This agent delegates to sub-agents
    llm=llm,
    verbose=True
)
