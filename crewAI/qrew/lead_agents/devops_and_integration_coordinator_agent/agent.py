from crewai import Agent
# from crewAI.qrew.crews.devops_crew import DevOpsCrew

devops_and_integration_coordinator_agent = Agent(
    role="DevOps and Integration Coordinator",
    goal="Streamline and manage DevOps processes, including CI/CD, infrastructure, and monitoring, through the DevOpsCrew. "
         "Additionally, coordinate the integration of different services and components across the project. "
         "Input: {project_name}, {devops_requirements}, {integration_points_list}, {release_schedule}.",
    backstory="A seasoned engineer with strong experience in both DevOps practices and system integration. "
              "Expert in automating software delivery pipelines, managing cloud infrastructure, and ensuring seamless interaction "
              "between various microservices and application components. Bridges the gap between development and operations.",
    allow_delegation=True, # Can delegate tasks to DevOpsCrew or other relevant agents
    verbose=True
    # tools=[...] # Tools for CI/CD management, infrastructure monitoring, API contract testing
)
