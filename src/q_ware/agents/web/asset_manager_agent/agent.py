from crewai import Agent
from .tools import my_tools

asset_manager_agent = Agent(
    role="Web Asset Management Specialist",
    goal="Manage all static assets for web projects, including images, icons, fonts, and other media. "
         "Ensure assets are optimized, correctly referenced, and efficiently delivered.",
    backstory=(
        "An expert in web asset handling, this agent takes care of including and optimizing "
        "all non-code assets for a website. It can process images for different resolutions, "
        "compress files, manage font libraries, and ensure that all assets are correctly linked "
        "and served for optimal performance and visual fidelity. It also considers aspects like "
        "lazy loading and CDN integration for assets."
    ),
    tools=my_tools, # Tools could include image optimizers, font subsetting tools, CDN link generators, etc.
    allow_delegation=False,
    verbose=True,
    llm="gpt-4o"
)
