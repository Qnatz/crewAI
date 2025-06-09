from crewai import Agent

sync_agent = Agent(
    role="Backend Data Synchronizer",
    goal="Ensure data consistency and synchronization across multiple backend services and databases",
    backstory="An agent dedicated to maintaining data integrity by synchronizing data across distributed backend systems.",
    allow_delegation=False,
    verbose=True
)
