from crewai import Agent
from q_ware.orchestrators.tech_stack_committee.tools.documentation_tools import MarkdownWriterTool

DocumentationWriterAgent = Agent(
    role='Technical Documentation Specialist',
    goal='Document the finalized tech stack in clear, professional Markdown format for team use',
    backstory=(
        'An expert technical writer responsible for making engineering decisions easily digestible for onboarding and planning.'
    ),
    tools=[MarkdownWriterTool()], # Now uses the correctly imported tool
    allow_delegation=False,
    llm="gemini/gemini-1.5-flash-latest",
    verbose=True
)
