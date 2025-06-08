from crewai import Crew, Task
# Ensure agent import paths are correct, pointing to their location in orchestrators/tech_stack_committee/agents/
from q_ware.orchestrators.tech_stack_committee.agents.stack_advisor_agent import StackAdvisorAgent
from q_ware.orchestrators.tech_stack_committee.agents.constraint_checker_agent import ConstraintCheckerAgent
from q_ware.orchestrators.tech_stack_committee.agents.documentation_writer_agent import DocumentationWriterAgent

class TechVettingCouncilCrew:
    def __init__(self, project_idea: str, constraints: str):
        self.project_idea = project_idea
        self.constraints = constraints
        # Note: CrewAI agents are typically passed as instances, not classes.
        # The user's example `agents=[StackAdvisorAgent, ...]` implies passing classes.
        # However, standard CrewAI practice is `agents=[StackAdvisorAgent(), ...]`.
        # For now, I will follow the user's example literally but this might need adjustment
        # if CrewAI expects instantiated agents.
        # Let's assume these agents have default constructors that work this way or CrewAI handles it.
        # If not, they would need to be instantiated: StackAdvisorAgent(), etc.
        self.crew = Crew(
            name="TechVettingCouncilCrew", # Added a name for the crew
            agents=[
                StackAdvisorAgent,
                ConstraintCheckerAgent,
                DocumentationWriterAgent
            ],
            tasks=[
                Task(
                    agent=StackAdvisorAgent, # Agent class
                    description=f"Propose a tech stack for: {self.project_idea}"
                ),
                Task(
                    agent=ConstraintCheckerAgent, # Agent class
                    description=f"Validate the proposal against: {self.constraints}"
                ),
                Task(
                    agent=DocumentationWriterAgent, # Agent class
                    description="Write TECH_STACK.md from the validated proposal"
                )
            ],
            verbose=True
        )

    def run(self):
        return self.crew.kickoff()
