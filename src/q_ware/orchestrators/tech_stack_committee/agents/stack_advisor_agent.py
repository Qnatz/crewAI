from crewai import Agent
from q_ware.orchestrators.tech_stack_committee.tools.tech_stack_tools import TechResearchTool

StackAdvisorAgent = Agent(
    role='Technology Advisor',
    goal='Recommend the most suitable technologies for frontend, backend, database, and infrastructure',
    backstory=(
        'An experienced full-stack architect who keeps up with the latest tools and best practices in the software industry. '
        'You prioritize scalability, maintainability, and alignment with business goals.'
    ),
    tools=[TechResearchTool()], # Now uses the correctly imported tool
    allow_delegation=False,
    verbose=True
)
