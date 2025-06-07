from crewai import Crew, Task
# Adjust agent import paths
from q_ware.orchestrators.tech_stack_committee.agents.stack_advisor_agent import StackAdvisorAgent
from q_ware.orchestrators.tech_stack_committee.agents.constraint_checker_agent import ConstraintCheckerAgent
from q_ware.orchestrators.tech_stack_committee.agents.documentation_writer_agent import DocumentationWriterAgent

def run_tech_stack_committee(project_idea: str, constraints: str):
    # Task 1: Generate tech stack recommendation
    recommendation_task = Task(
        description=f"Based on the project idea: '{project_idea}', propose a full stack including frontend, backend, DB, and infrastructure.",
        expected_output="A tech stack list with justifications for each component",
        agent=StackAdvisorAgent
    )

    # Task 2: Validate the stack against constraints
    validation_task = Task(
        description=(
            f"Given the tech stack proposal, evaluate its feasibility using these constraints: {constraints}. "
            "Highlight any conflicts or risks and suggest adjustments if needed."
        ),
        expected_output="A feasibility report outlining constraint compliance and needed adjustments",
        agent=ConstraintCheckerAgent
    )

    # Task 3: Document the final decision
    documentation_task = Task(
        description="Using the refined and validated stack, create a Markdown doc with a clean list of tools and reasons for each.",
        expected_output="A Markdown file titled `TECH_STACK.md` with full stack explanation",
        agent=DocumentationWriterAgent
    )

    crew = Crew(
        agents=[StackAdvisorAgent, ConstraintCheckerAgent, DocumentationWriterAgent],
        tasks=[recommendation_task, validation_task, documentation_task],
        verbose=True
    )

    return crew.kickoff()
