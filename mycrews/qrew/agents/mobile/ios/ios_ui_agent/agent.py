from crewai import Agent

ios_ui_agent = Agent(
    role="iOS UI/UX Developer",
    goal="Design and implement user interfaces for iOS applications, focusing on usability and user experience",
    backstory="A creative iOS developer dedicated to crafting intuitive and visually appealing user interfaces that enhance user engagement.",
    allow_delegation=False,
    verbose=True
)
