from crewai import Agent
# The tool import path will be adjusted later. For now, use the path from the user's example.
# from tools.tech_stack_tools import TechResearchTool
# Placeholder for now, will be replaced:
from crewai_tools import BaseTool # Placeholder, real tool will be different

# Define a placeholder tool if the real one isn't available yet for import validation
class TechResearchTool(BaseTool):
    name: str = "Placeholder Tech Research Tool"
    description: str = "A placeholder tool."
    def _run(self, argument: str) -> str:
        return "Placeholder execution"


StackAdvisorAgent = Agent(
    role='Technology Advisor',
    goal='Recommend the most suitable technologies for frontend, backend, database, and infrastructure',
    backstory=(
        'An experienced full-stack architect who keeps up with the latest tools and best practices in the software industry. '
        'You prioritize scalability, maintainability, and alignment with business goals.'
    ),
    tools=[TechResearchTool()],
    allow_delegation=False,
    verbose=True
)
