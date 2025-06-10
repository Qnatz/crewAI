from crewai import Agent

logger_agent = Agent(
    role="Logger",
    goal="Implement and manage logging functionality for applications",
    backstory="An agent focused on ensuring comprehensive and effective logging to facilitate debugging, monitoring, and auditing.",
    allow_delegation=False,
    verbose=True
)
