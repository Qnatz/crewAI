from crewai import Agent
from q_ware.orchestrators.tech_stack_committee.tools.documentation_tools import MarkdownWriterTool
from q_ware.llm_config import get_llm

llm = get_llm()
DocumentationWriterAgent = Agent(
    role='Technical Documentation Specialist',
    goal='Document the finalized tech stack in clear, professional Markdown format for team use',
    backstory=(
        'An expert technical writer responsible for making engineering decisions easily digestible for onboarding and planning.'
    ),
    tools=[MarkdownWriterTool()], # Now uses the correctly imported tool
    allow_delegation=False,
    llm=llm,
    verbose=True
)
