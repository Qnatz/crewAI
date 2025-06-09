from crewai import Agent

offline_sync_agent = Agent(
    role="Offline Data Synchronizer",
    goal="Manage data synchronization between local storage and remote servers when an internet connection is available",
    backstory="An agent dedicated to ensuring data consistency between offline local storage and online backend systems by managing data synchronization processes.",
    allow_delegation=False,
    verbose=True
)
