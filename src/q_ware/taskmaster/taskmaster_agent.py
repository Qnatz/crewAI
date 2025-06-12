from crewai import Task # Assuming Task is used for internal representation
# Import the refined TechVettingCouncilCrew class
from q_ware.orchestrators.tech_stack_committee.crews.tech_vetting_council_crew import TechVettingCouncilCrew
# Import the CodeWritingCrew class
from q_ware.crews.utility_crews.code_writing_crew import CodeWritingCrew
# Import the FinalAssemblyCrew class
from q_ware.crews.utility_crews.final_assembly_crew import FinalAssemblyCrew
# Import the CodeWriterAgent instance for the default handler (as per original structure, though CodeWritingCrew is preferred)
# from q_ware.agents.dev_utilities.code_writer_agent.agent import code_writer_agent
# Import the actual ExecutionManagerCrew
from q_ware.orchestrators.execution_manager_agent import ExecutionManagerCrew


class TaskmasterAgent:
    def __init__(self, mode: str = 'default'):
        self.mode = mode
        # In load_crews, we store the classes, not instances yet
        self.active_crew_classes = self.load_crew_classes()

    def load_crew_classes(self):
        return {
            "tech_vetting": TechVettingCouncilCrew,
            "execution_manager": ExecutionManagerCrew,
            "final_assembly": FinalAssemblyCrew,
            # Add more crew classes as they come online
        }

    def route_task(self, task_description: str, task_context: dict = None): # Changed to task_description and optional context
        """Smart routing logic based on task description or other properties."""
        # Simple keyword routing for now, can be enhanced with LLM parsing / intent recognition
        if "tech stack" in task_description.lower() or "technology" in task_description.lower():
            crew_cls = self.active_crew_classes["tech_vetting"]
            # TechVettingCouncilCrew expects project_idea and constraints
            # We need to map task_description and task_context to these.
            # Assuming task_description is project_idea and constraints are in task_context
            project_idea = task_description
            constraints = task_context.get("constraints", "") if task_context else ""
            crew_instance = crew_cls(project_idea=project_idea, constraints=constraints)
            return crew_instance.run()
        elif "execute" in task_description.lower() or "implement" in task_description.lower():
            crew_cls = self.active_crew_classes["execution_manager"]
            project_plan = task_context.get("project_plan") if task_context else None

            if not isinstance(project_plan, dict):
                # Fallback: create a minimal plan from task_description if no dict plan is provided
                print(f"Warning: No detailed project_plan (dict) provided for execution task. Using task_description as summary for ExecutionManagerCrew.")
                project_plan = {
                    "project_name": "AdHoc Execution Project",
                    "summary": task_description,
                    # Indicate that specific requirements are not broken down yet
                    "backend_requirements": "As per overall summary" if "backend" in task_description.lower() else None,
                    "frontend_requirements": "As per overall summary" if "frontend" in task_description.lower() or "web" in task_description.lower() else None,
                    "mobile_requirements": "As per overall summary" if "mobile" in task_description.lower() else None,
                    # Add other potential keys based on keywords in task_description or leave them out
                }
                # Filter out None values to keep plan clean
                project_plan = {k: v for k, v in project_plan.items() if v is not None}

            if not project_plan: # If it's still None or empty after fallback attempt
                 error_msg = "Error: Execution task routed, but no valid project_plan (dict) found in context, and could not form basic plan from description."
                 print(error_msg)
                 return error_msg # Or raise an exception

            crew_instance = crew_cls(project_plan=project_plan)
            return crew_instance.run()
        elif "assemble" in task_description.lower() or "finalize" in task_description.lower() or "package solution" in task_description.lower():
            crew_cls = self.active_crew_classes["final_assembly"]
            # FinalAssemblyCrew expects assembly_instructions
            assembly_instructions = task_description # Or derive from context
            crew_instance = crew_cls(assembly_instructions=assembly_instructions)
            return crew_instance.run()
        else:
            # Fallback to default_handler using CodeWritingCrew
            return self.default_handler(task_description)

    def default_handler(self, prompt: str):
        # Use CodeWritingCrew for generic code writing tasks
        crew = CodeWritingCrew(prompt=prompt)
        return crew.run()

    def run(self, prompt: str, context: dict = None): # Added context to run method
        # The Taskmaster's run method now directly calls route_task
        # No need to create a crewai.Task object just to pass the description
        return self.route_task(task_description=prompt, task_context=context)
