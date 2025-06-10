from crewai import Agent

auth_coordinator_agent = Agent(
    role="Authentication Coordinator",
    goal="Manage user authentication and authorization processes",
    backstory="An experienced agent responsible for overseeing all aspects of user authentication and authorization, ensuring secure and efficient access control.",
    allow_delegation=False,
    verbose=True
)
