from crewai import Agent
from q_ware.orchestrators.tech_stack_committee.tools.constraints_tools import ConstraintValidatorTool

# LLM Interaction Note:
# The `ConstraintValidatorTool` used by this agent expects its `proposal` argument as a direct string.
# The agent's LLM must be guided (e.g., through tool description or prompt engineering)
# to provide the proposal as a single string, not a dictionary like `{"description": "..."}`.
# The tool's description has been updated to reflect this.
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
