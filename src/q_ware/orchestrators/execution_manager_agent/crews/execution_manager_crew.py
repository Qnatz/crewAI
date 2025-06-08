from crewai import Crew, Task
# Import the coordinator agents this crew will delegate to
from q_ware.agents.backend.agent import backend_coordinator_agent
from q_ware.agents.web.agent import web_project_coordinator_agent
from q_ware.agents.mobile.agent import mobile_project_coordinator_agent
from q_ware.agents.offline.agent import offline_support_coordinator_agent
from q_ware.agents.devops.agent import devops_and_integration_coordinator_agent
# Potentially, other coordinators or specialized agents

# Placeholder for any tools specific to the ExecutionManagerCrew itself
# from ..tools import execution_manager_tools # Example if tools are defined

# This crew might have its own sub-agents for planning or monitoring.
# For now, we'll assume it directly uses the imported coordinators.

class ExecutionManagerCrew:
    def __init__(self, project_plan: dict): # Expects a project plan (e.g., from ProjectArchitect)
        self.project_plan = project_plan
        self.name = "ProjectExecutionCrew" # Give the crew a name

        # These are the coordinator agents that the Execution Manager will delegate to.
        # CrewAI expects agent instances.
        self.coordinators = [
            backend_coordinator_agent,
            web_project_coordinator_agent,
            mobile_project_coordinator_agent,
            offline_support_coordinator_agent,
            devops_and_integration_coordinator_agent
        ]

        # The tasks below are conceptual representations of what this crew would manage.
        # The actual creation and assignment of these tasks to the coordinators
        # would be part of the .run() method's logic, potentially dynamically generated
        # based on the self.project_plan.

        self.managed_tasks = self._create_tasks_from_plan(project_plan)

        self.crew = Crew(
            name=self.name,
            agents=self.coordinators, # The agents this crew directly manages/assigns tasks to.
            tasks=self.managed_tasks, # These tasks would be assigned to the coordinators.
            verbose=True
        )

    def _create_tasks_from_plan(self, project_plan: dict) -> list:
        """
        Parses the project plan and creates high-level tasks for each coordinator.
        This is a simplified placeholder. A real implementation would be more sophisticated,
        dynamically assigning tasks based on plan content and coordinator capabilities.
        """
        tasks = []

        # Example: Iterate through plan sections and create tasks
        if project_plan.get("backend_requirements"):
            tasks.append(Task(
                description=f"Develop backend features as per plan: {project_plan['backend_requirements']}",
                expected_output="Fully functional and tested backend components.",
                agent=backend_coordinator_agent
            ))
        if project_plan.get("frontend_requirements"): # Assuming web frontend
            tasks.append(Task(
                description=f"Develop web frontend as per plan: {project_plan['frontend_requirements']}",
                expected_output="Fully functional and tested web frontend.",
                agent=web_project_coordinator_agent
            ))
        if project_plan.get("mobile_requirements"):
            tasks.append(Task(
                description=f"Develop mobile applications as per plan: {project_plan['mobile_requirements']}",
                expected_output="Fully functional and tested mobile applications for Android and iOS.",
                agent=mobile_project_coordinator_agent
            ))
        if project_plan.get("offline_requirements"):
             tasks.append(Task(
                description=f"Implement offline capabilities as per plan: {project_plan['offline_requirements']}",
                expected_output="Robust offline functionality implemented.",
                agent=offline_support_coordinator_agent
            ))
        if project_plan.get("devops_requirements"):
            tasks.append(Task(
                description=f"Set up CI/CD, infrastructure, and integration testing as per plan: {project_plan['devops_requirements']}",
                expected_output="CI/CD pipelines, configured environments, and integration test suite.",
                agent=devops_and_integration_coordinator_agent
            ))
        # ... and so on for other parts of the plan

        if not tasks: # Fallback if plan is not detailed enough for specific tasks yet
            tasks.append(Task(
                description=f"Execute overall project plan: {project_plan.get('summary', 'details not provided')}",
                expected_output="Completed project components as per the overall plan.",
                # No specific agent, taskmaster might need to assign this or it's a sequential crew.
                # For now, let's assign to the first coordinator as a placeholder if no specific tasks.
                # This part needs refinement based on how Taskmaster uses this crew.
                # A better approach would be for ExecutionManager to have its own planning agent.
                agent=self.coordinators[0] if self.coordinators else None
            ))
        return tasks

    def run(self):
        """
        Kicks off the execution of the project plan by managing the defined tasks
        and coordinating the involved agents.
        """
        if not self.managed_tasks or not self.crew.tasks: # Check self.crew.tasks as well
            print(f"ExecutionManagerCrew ({self.name}): No tasks derived from the project plan or tasks list is empty. Cannot run.")
            return "No tasks to execute based on the project plan."

        print(f"ExecutionManagerCrew ({self.name}) starting with project plan: {self.project_plan.get('summary', 'details not provided')}")
        # The actual execution logic will involve kicking off its internal crew.
        # This crew instance (self.crew) is composed of the coordinator agents and the tasks for them.
        result = self.crew.kickoff()
        print(f"ExecutionManagerCrew ({self.name}) finished.")
        return result
