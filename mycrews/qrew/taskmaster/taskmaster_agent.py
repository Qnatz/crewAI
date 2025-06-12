import json
from pathlib import Path
from crewai import Agent, Task # Added Task import
from ..tools import knowledge_base_tool_instance # Kept existing import
from ..llm_config import get_llm_for_agent # Kept existing import
from ..project_manager import get_or_create_project # Added new import

agent_identifier = "taskmaster_agent"
specific_llm = get_llm_for_agent(agent_identifier)

PROJECT_CHECKPOINT_FILENAME = ".taskmaster_checkpoint.json"

class TaskMasterGeneralCoordinatorAgent(Agent): # Inherit from Agent
    def __init__(self, **kwargs): # Add __init__
        super().__init__(
            role="TaskMaster General Coordinator and Project Manager",
            goal="Receive, interpret, and decompose high-level user requests or project goals into a structured plan of deliverables. "
                 "Manage the lifecycle of these projects, tracking progress and ensuring successful completion. "
                 "Delegate major components of this plan to appropriate orchestrator agents or specialized Lead Agents for execution. "
                 "Ensure a clear path from initial request to final delivery, maintaining project state and enabling resumability. "
                 "Input: {user_request} (e.g., 'develop fitness app'), {project_goal_statement}, {priority_level}, {expected_outcome_description}.",
            backstory="The central intelligence of the Qrew system, responsible for initial request processing, strategic delegation, and comprehensive project lifecycle management. "
                      "The TaskMaster doesn't just initiate tasks but actively manages ongoing projects, tracking deliverables, "
                      "handling errors, and ensuring that all project-related data is stored and resumable. It ensures that the right agents "
                      "and crews are mobilized and that project progress is meticulously recorded.",
            tools=[knowledge_base_tool_instance],
            llm=specific_llm,
            allow_delegation=True,
            verbose=True,
            **kwargs # Pass other kwargs to parent
        )

    def _resolve_project_path(self, project_path_str: str) -> Path:
        # Assuming project_manager.py is in mycrews/qrew/ and this agent might be elsewhere,
        # but project_info['path'] from get_or_create_project is already a relative path
        # from the qrew directory (e.g., "projects/some_project_id").
        # So, we need to make it relative to the script that's *using* project_manager.
        # The path stored by project_manager is Path(__file__).parent / "projects" / key
        # which means it's already relative to mycrews/qrew.
        # If TaskMaster is also in mycrews/qrew, then Path(project_path_str) is fine.
        # Let's assume TaskMaster is in mycrews/qrew/taskmaster for now.
        # The path from get_or_create_project is 'projects/some_project_id'
        # Path(__file__).parent.parent gives 'mycrews/qrew'
        base_path = Path(__file__).parent.parent # This should be mycrews/qrew
        return (base_path / project_path_str).resolve()

    def load_project_progress(self, project_checkpoint_file: Path) -> dict:
        if project_checkpoint_file.exists():
            try:
                return json.loads(project_checkpoint_file.read_text())
            except json.JSONDecodeError:
                # Handle corrupted or empty file
                pass # Return default progress below
        return {"completed_deliverables": {}, "results": {}, "errors": {}}

    def save_project_progress(self, project_checkpoint_file: Path, progress: dict):
        project_checkpoint_file.write_text(json.dumps(progress, indent=4))
        print(f"Project progress saved to {project_checkpoint_file}")

    def orchestrate_project(self, user_request: str, project_deliverables_list: list = None):
        print(f"TaskMaster starting orchestration for: {user_request}")

        project_info = get_or_create_project(name=user_request)
        print(f"Project info: {project_info}")

        # Path returned by get_or_create_project is relative to mycrews/qrew/
        # e.g. projects/fitness_app_xyz
        # We need the absolute path.
        # Assuming this file (taskmaster_agent.py) is in mycrews/qrew/taskmaster/
        # then Path(__file__).parent.parent is mycrews/qrew/
        qrew_base_path = Path(__file__).parent.parent
        absolute_project_path = (qrew_base_path / project_info["path"]).resolve()
        print(f"Absolute project path: {absolute_project_path}")

        project_checkpoint_file = absolute_project_path / PROJECT_CHECKPOINT_FILENAME
        project_progress = self.load_project_progress(project_checkpoint_file)

        # Replace this with actual deliverables based on user_request or a defined plan
        if project_deliverables_list is None:
            # Example: Dynamically determine deliverables or use a default set
            # This should ideally come from another agent (e.g., ProjectArchitect) or be predefined
            project_deliverables_list = [
                "define_user_stories",
                "ui_ux_design_spec_v1",
                "develop_backend_api",
                "develop_frontend_app",
                "final_testing_and_qa"
            ]

        print(f"Project deliverables: {project_deliverables_list}")

        for deliverable_key in project_deliverables_list:
            print(f"Processing deliverable: {deliverable_key}...")
            if project_progress["completed_deliverables"].get(deliverable_key):
                print(f"Deliverable '{deliverable_key}' already completed. Skipping.")
                continue

            current_project_context = {
                "project_name": project_info["name"],
                "project_id": project_info["id"],
                "project_path": str(absolute_project_path),
                "deliverable_key": deliverable_key,
                "all_deliverables": project_deliverables_list,
                "project_progress_file": str(project_checkpoint_file)
            }

            # --- Dependency Handling Example ---
            if deliverable_key == "ui_ux_design_spec_v1":
                if project_progress["results"].get("define_user_stories"):
                    current_project_context["user_stories_input"] = project_progress["results"]["define_user_stories"]
                else:
                    print(f"Dependency not met: 'define_user_stories' results not found for '{deliverable_key}'. Skipping.")
                    project_progress["errors"][deliverable_key] = "Dependency 'define_user_stories' not met."
                    self.save_project_progress(project_checkpoint_file, project_progress)
                    continue # Or handle more gracefully

            try:
                # --- Replace with actual delegation logic ---
                # This is where TaskMaster would create a Task and assign it to another agent/crew
                # Example:
                # task_description = f"Execute deliverable: {deliverable_key} for project {project_info['name']}"
                # placeholder_agent = Agent(role="Placeholder Agent", goal="Execute a task", backstory="I am a placeholder.") # Define or get actual agent
                # task = Task(description=task_description, agent=placeholder_agent, expected_output="Result of the deliverable")
                # result = self.delegate_task(task, current_project_context) # You'll need a method to delegate tasks

                # Simulating execution and result for now:
                print(f"Simulating execution of deliverable: {deliverable_key} with context: {current_project_context}")
                if deliverable_key == "define_user_stories":
                    result = {"user_stories": ["As a user, I can log in.", "As a user, I can view my profile."]}
                elif deliverable_key == "ui_ux_design_spec_v1":
                    result = {"design_document_link": "/path/to/design_v1.pdf"}
                else:
                    result = f"Successfully completed {deliverable_key}"
                # --- End of simulated execution ---

                project_progress["results"][deliverable_key] = result
                project_progress["completed_deliverables"][deliverable_key] = True
                print(f"Deliverable '{deliverable_key}' completed successfully.")

            except Exception as e:
                print(f"Error executing deliverable '{deliverable_key}': {e}")
                project_progress["errors"][deliverable_key] = str(e)

            self.save_project_progress(project_checkpoint_file, project_progress)

        print(f"All deliverables processed for project: {user_request}")
        print(f"Final project progress: {project_progress}")
        return project_progress

    def delegate_task(self, task: Task, context: dict): # Add this method
        # This is a simplified delegation. In a real scenario, you might add context to task or agent
        # For CrewAI, tasks are typically executed by a Crew.
        # You might need to dynamically create a crew or have pre-defined crews.
        print(f"TaskMaster delegating task: {task.description} with context {context}")
        # The context should be available to the agent executing the task.
        # One way is to pass it in the task's parameters or if the agent's method accepts it.
        # For now, this is a placeholder. The actual execution would be:
        # result = crew.kickoff(inputs=context) or agent.execute_task(task)
        # This part needs to be aligned with how CrewAI tasks are given context.
        # Often, the context is passed as inputs to a crew's kickoff.
        # task.execute(context=context) # This is one way if the task's agent can use it.
        return f"Result for {task.description}" # Placeholder


# Instantiate the agent
taskmaster_agent_instance = TaskMasterGeneralCoordinatorAgent()

# Example of how you might call it (for testing purposes, remove for production agent definition)
# if __name__ == "__main__":
#     # Ensure project_manager.py can be found if running this directly
#     # This setup is for direct execution testing.
#     # In a real CrewAI setup, the agent is part of a crew and tasks are assigned.
#     print("Running TaskMaster directly for testing...")
#     # Example project
#     project_name = "example_fitness_app_project"
#     deliverables = [
#         "define_user_stories",
#         "ui_ux_design_spec_v1",
#         "setup_project_structure",
#         "develop_backend_user_auth",
#         "develop_frontend_login_page"
#     ]
#     final_status = taskmaster_agent_instance.orchestrate_project(
#         user_request=project_name,
#         project_deliverables_list=deliverables
#     )
#     print("\nFinal Project Status:")
#     print(json.dumps(final_status, indent=2))

# Replace the old `taskmaster_agent` instance with the new class instance or structure
# For now, we'll keep the old name for the instance if other parts of the system expect it.
taskmaster_agent = taskmaster_agent_instance
