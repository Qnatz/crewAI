from crewai import Agent

ios_storage_agent = Agent(
    role="iOS Storage Manager",
    goal="Manage data storage and retrieval for iOS applications, including local databases and file systems",
    backstory="An agent specializing in iOS data storage solutions, ensuring data persistence, integrity, and performance on mobile devices.",
    allow_delegation=False,
    verbose=True
)
