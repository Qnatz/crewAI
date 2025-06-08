from crewai import Agent
from q_ware.orchestrators.tech_stack_committee.tools.constraints_tools import ConstraintValidatorTool

ConstraintCheckerAgent = Agent(
    role='Constraint Checker',
    goal='Ensure that the proposed stack aligns with project constraints like budget, team skills, performance, and security',
    backstory=(
        'A pragmatic systems engineer who assesses technology recommendations against hard project constraints. '
        'You ensure feasibility and reduce risk.'
    ),
    tools=[ConstraintValidatorTool()], # Now uses the correctly imported tool
    allow_delegation=False,
    llm="gemini/gemini-1.5-flash-latest",
    verbose=True
)
