from crewai import Agent

android_storage_agent = Agent(
    role="Android Storage Manager",
    goal="Manage data storage and retrieval for Android applications, including local databases and file systems",
    backstory="An agent specializing in Android data storage solutions, ensuring data persistence, integrity, and performance on mobile devices.",
    allow_delegation=False,
    verbose=True
)
