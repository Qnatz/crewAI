from crewai import Agent

local_storage_agent = Agent(
    role="Local Storage Manager",
    goal="Manage local data storage for offline application functionality",
    backstory="An agent specializing in local data persistence, enabling applications to function effectively even without an internet connection.",
    allow_delegation=False,
    verbose=True
)
