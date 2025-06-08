from crewai import Crew, Task, Agent
from typing import List, Dict, Any

# Import the coordinator agent instances
from q_ware.agents.backend.agent import backend_coordinator_agent
from q_ware.agents.web.agent import web_project_coordinator_agent
from q_ware.agents.mobile.agent import mobile_project_coordinator_agent
from q_ware.agents.offline.agent import offline_support_coordinator_agent
from q_ware.agents.devops.agent import devops_and_integration_coordinator_agent

# Placeholder for any tools specific to the ExecutionManagerCrew itself
# from ..tools import some_execution_manager_tool

# This crew might have its own sub-agents for detailed planning or monitoring in a future phase.
# For now, it directly uses the imported coordinator agents.

class ExecutionManagerCrew:
    def __init__(self, project_plan: Dict[str, Any]):
        """
        Initializes the ExecutionManagerCrew with a project plan.
        The project_plan is expected to be a dictionary with keys like
        'project_name', 'summary', 'backend_requirements', 'frontend_requirements', etc.
        """
        if not isinstance(project_plan, dict):
            raise ValueError("ExecutionManagerCrew expects project_plan to be a dictionary.")

        self.project_plan = project_plan
        self.project_name = project_plan.get("project_name", "Unnamed Project")
        self.crew_name = f"{self.project_name.replace(' ', '')}ExecutionCrew"

        # These are the coordinator agents that the Execution Manager will delegate to.
        # These are imported instances.
        self.coordinator_agents: List[Agent] = [
            backend_coordinator_agent,
            web_project_coordinator_agent,
            mobile_project_coordinator_agent,
            offline_support_coordinator_agent,
            devops_and_integration_coordinator_agent
        ]

        self.managed_tasks: List[Task] = self._create_tasks_from_plan()

        # The internal crew is now initialized just before running,
        # as tasks might be dynamic or depend on initial setup.
        # However, for CrewAI structure, tasks and agents are usually defined at init.
        # Let's stick to defining it at init.
        if not self.managed_tasks:
            print(f"Warning: No specific tasks generated for project '{self.project_name}'. Execution might be limited.")
            # Create a generic task if none are generated to avoid Crew errors,
            # or handle this more gracefully in run().
            # This generic task would ideally be assigned to a general-purpose coordinator or an initial phase agent.
            # For now, if no tasks, the crew.kickoff() might not work as expected or do nothing.
            # Let's ensure there's at least one task if there are agents.
            if not self.coordinator_agents:
                 raise ValueError("ExecutionManagerCrew: No coordinator agents available to assign tasks.")
            # This generic task is a fallback and ideally should not be hit if project_plan is well-defined.
            self.managed_tasks.append(Task(
                description=f"Oversee and ensure successful completion of all aspects of '{self.project_name}' as per high-level plan: {self.project_plan.get('summary', 'No summary provided.')}",
                expected_output=f"All project components for '{self.project_name}' delivered and integrated.",
                agent=self.coordinator_agents[0] # Assign to the first available coordinator as a general task
            ))


        self.crew = Crew(
            name=self.crew_name,
            agents=self.coordinator_agents,
            tasks=self.managed_tasks,
            verbose=True
            # memory=True, # Example: enable memory for the crew if needed
            # manager_llm=ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7), # Example: dedicated manager LLM
        )

    def _create_tasks_from_plan(self) -> List[Task]:
        """
        Parses the project plan and creates high-level tasks for each coordinator.
        This version creates tasks if specific requirement keys are found in the project_plan.
        """
        tasks: List[Task] = []
        plan = self.project_plan

        if plan.get("backend_requirements"):
            tasks.append(Task(
                description=f"Project: '{self.project_name}'. Orchestrate and develop all backend systems and APIs based on requirements: {plan['backend_requirements']}",
                expected_output="Fully functional, tested, and documented backend components and APIs.",
                agent=backend_coordinator_agent
            ))
        if plan.get("frontend_requirements") or plan.get("web_requirements"): # allow 'web_requirements' too
            web_req = plan.get("frontend_requirements", plan.get("web_requirements"))
            tasks.append(Task(
                description=f"Project: '{self.project_name}'. Coordinate the design and development of the project website and web applications based on requirements: {web_req}",
                expected_output="A fully functional, responsive, and tested website/web application.",
                agent=web_project_coordinator_agent
            ))
        if plan.get("mobile_requirements"):
            tasks.append(Task(
                description=f"Project: '{self.project_name}'. Coordinate the design and development of Android and iOS mobile applications based on requirements: {plan['mobile_requirements']}",
                expected_output="Fully functional, tested, and platform-compliant mobile applications for Android and iOS.",
                agent=mobile_project_coordinator_agent
            ))
        if plan.get("offline_requirements"):
             tasks.append(Task(
                description=f"Project: '{self.project_name}'. Coordinate the implementation of offline-first capabilities, including local storage and data synchronization, based on requirements: {plan['offline_requirements']}",
                expected_output="Robust and seamless offline functionality integrated into relevant applications.",
                agent=offline_support_coordinator_agent
            ))
        if plan.get("devops_requirements"):
            tasks.append(Task(
                description=f"Project: '{self.project_name}'. Manage CI/CD pipelines, environment configurations, containerization, and overall integration testing based on requirements: {plan['devops_requirements']}",
                expected_output="Automated CI/CD pipelines, well-configured environments, containerized applications (if applicable), and a comprehensive integration test suite.",
                agent=devops_and_integration_coordinator_agent
            ))

        return tasks

    def run(self) -> str:
        """
        Kicks off the execution of the project plan by managing the defined tasks
        and coordinating the involved agents via its internal Crew.
        """
        if not self.managed_tasks: # Should be caught by the __init__ logic now
            print(f"ExecutionManagerCrew ({self.crew_name}): No tasks were generated from the project plan. Cannot run.")
            return "ExecutionManagerCrew: No tasks to execute. Project plan might be underspecified for task generation."

        print(f"ExecutionManagerCrew ({self.crew_name}) starting execution for project: '{self.project_name}'.")
        print(f"Project Summary: {self.project_plan.get('summary', 'No summary provided.')}")
        print(f"Number of high-level tasks generated: {len(self.managed_tasks)}")

        result = self.crew.kickoff()

        print(f"ExecutionManagerCrew ({self.crew_name}) finished execution for project: '{self.project_name}'.")
        return result
