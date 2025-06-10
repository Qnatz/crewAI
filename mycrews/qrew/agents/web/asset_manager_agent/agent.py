from crewai import Agent

asset_manager_agent = Agent(
    role="Web Asset Manager",
    goal="Manage and optimize static assets (images, CSS, JavaScript) for web applications",
    backstory="An agent focused on efficient asset management, ensuring fast loading times and optimal performance for web applications.",
    allow_delegation=False,
    verbose=True
)
