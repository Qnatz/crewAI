from crewai import Agent
from ...llm_config import get_llm_for_agent
# from mycrews.qrew.crews.backend_development_crew import BackendDevelopmentCrew

# Use the agent's role or a unique key for the lookup
agent_identifier = "backend_project_coordinator_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

backend_project_coordinator_agent = Agent(
    role="Backend Project Coordinator",
    goal="Oversee and manage the BackendDevelopmentCrew to build and maintain robust, scalable, and secure backend services and APIs. "
         "Ensure alignment with architectural guidelines and project timelines. "
         "Input: {project_scope}, {backend_requirements}, {api_specifications}, {architecture_docs}, {delivery_milestones}.",
    backstory="A highly organized project manager with extensive experience in backend systems development. "
              "Proficient in agile methodologies, API design principles, database management, and cloud infrastructure. "
              "Effectively leads backend teams to deliver high-performance services.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=True, # Can delegate tasks to the BackendDevelopmentCrew
    verbose=True
    # tools=[...] # Tools for API testing, performance monitoring, task management
)
