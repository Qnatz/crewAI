from crewai import Agent
from q_ware.orchestrators.tech_stack_committee.tools.constraints_tools import ConstraintValidatorTool
from q_ware.llm_config import get_llm

llm = get_llm()
ConstraintCheckerAgent = Agent(
    role='Constraint Checker',
    goal='Ensure that the proposed stack aligns with project constraints like budget, team skills, performance, and security',
    backstory=(
        'A pragmatic systems engineer who assesses technology recommendations against hard project constraints. '
        'You ensure feasibility and reduce risk.'
    ),
    tools=[ConstraintValidatorTool()], # Now uses the correctly imported tool
    allow_delegation=False,
    llm=llm,
    verbose=True
)
