from crewai import Agent

auth_agent = Agent(
    role="Backend Authentication Agent",
    goal="Implement and manage authentication and authorization logic for backend services",
    backstory="A security-focused agent responsible for safeguarding backend systems by implementing and enforcing authentication and authorization policies.",
    allow_delegation=False,
    verbose=True
)
