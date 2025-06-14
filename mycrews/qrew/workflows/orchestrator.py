import json # Added
from crewai import Crew, Task # Added
from ..taskmaster.taskmaster_agent import taskmaster_agent # Added
from .idea_to_architecture_flow import run_idea_to_architecture_workflow
from .crew_lead_workflow import run_crew_lead_workflow
from .subagent_execution_workflow import run_subagent_execution_workflow
from .final_assembly_workflow import run_final_assembly_workflow
from ..project_manager import ProjectStateManager # Adjusted import path

# Guardrail function for Taskmaster output
def validate_taskmaster_output(output: str) -> tuple[bool, any]: # Changed 'any' to 'str' for error message, any for data
    try:
        data = json.loads(output)
        if not isinstance(data, dict):
            return False, "Output must be a JSON dictionary."
        required_keys = ["project_name", "refined_brief", "is_new_project"]
        for key in required_keys:
            if key not in data:
                return False, f"Missing key in output: {key}"
        if not isinstance(data["project_name"], str) or not data["project_name"].strip():
            return False, "project_name must be a non-empty string."
        if not isinstance(data["refined_brief"], str) or not data["refined_brief"].strip():
            return False, "refined_brief must be a non-empty string."
        if not isinstance(data["is_new_project"], bool):
            return False, "is_new_project must be a boolean."
        return True, data # Return parsed data on success
    except json.JSONDecodeError:
        return False, "Output must be valid JSON."
    except Exception as e:
        return False, f"Validation error: {str(e)}"

class WorkflowOrchestrator:
    def __init__(self, project_name: str = None):
        self.initial_project_name_hint = project_name
        if project_name:
            self.state = ProjectStateManager(project_name)
        else:
            self.state = None # Will be initialized after taskmaster runs

        # The workflow functions themselves are expected to handle their inputs
        # and interact with ProjectStateManager if they need to load/save intermediate artifacts
        # specific to their internal steps, or check if they can be skipped.
        self.workflows = {
            "taskmaster": self.run_taskmaster_workflow,
            "architecture": run_idea_to_architecture_workflow,
            "crew_assignment": run_crew_lead_workflow,
            "subagent_execution": run_subagent_execution_workflow,
            "final_assembly": run_final_assembly_workflow
        }

    def run_taskmaster_workflow(self, inputs: dict):
        print("Executing Taskmaster workflow...")
        user_request = inputs.get("user_request", "")
        if not user_request:
            # This case should ideally be handled before calling this workflow,
            # but as a safeguard:
            print("Error: No user_request provided to Taskmaster workflow.")
            # Return a structure that indicates failure or default values
            # This matches the expected output structure but with error indication.
            return {
                "project_name": "error_no_user_request",
                "refined_brief": "Taskmaster failed: No user request was provided.",
                "is_new_project": False, # Default to False to avoid accidental new project creation
                "taskmaster_error": "No user_request provided"
            }

        taskmaster_task = Task(
            description=f"Process the following user request: '{user_request}'. "
                        f"Determine if this pertains to a new or existing project. "
                        f"If it's a new project, generate a unique and descriptive project name (e.g., based on key themes from the request, and ensure it's filesystem-safe). "
                        f"Then, create a refined project brief based on the request. "
                        f"You MUST use the 'knowledge_base_tool_instance' to check for existing projects or ideas if applicable, though the primary check for project name uniqueness will be handled by the ProjectStateManager based on the name you generate. "
                        f"Focus on understanding the core needs and deliverables.",
            agent=taskmaster_agent,
            expected_output="A JSON object containing: "
                            "'project_name' (string, unique and descriptive for new projects), "
                            "'refined_brief' (string, a concise summary and scope), "
                            "and 'is_new_project' (boolean, True if this is identified as a new project, False otherwise).",
            guardrail=validate_taskmaster_output,
            max_retries=1
        )

        # Create a temporary crew to execute this task
        # The llm for the crew will be inherited from the agent if not specified,
        # or we can assign the orchestrator's default llm if it had one.
        # For now, relying on agent's LLM.
        task_crew = Crew(
            agents=[taskmaster_agent],
            tasks=[taskmaster_task],
            verbose=True # Or False, depending on desired logging level
        )

        result = task_crew.kickoff()

        if result and hasattr(result, 'raw') and result.raw:
            # The guardrail `validate_taskmaster_output` returns the parsed data on success.
            # However, the `result.raw` from crewAI task output is typically the raw string.
            # We need to re-parse it here, or trust the guardrail completely.
            # The guardrail is designed to ensure it's valid if the task succeeded.
            try:
                # If guardrail ran, result.raw should be the validated JSON string.
                # If task failed after retries, result.raw might be an error or last attempt.
                # The guardrail should prevent non-JSON from being in .raw if task is_successful.
                # Let's assume if we are here, task was successful and .raw is the JSON string.
                parsed_output = json.loads(result.raw)
                return parsed_output
            except json.JSONDecodeError:
                print(f"Taskmaster output was not valid JSON despite guardrail: {result.raw}")
                # Fallback to error structure
                return {
                    "project_name": "error_taskmaster_output_invalid",
                    "refined_brief": f"Taskmaster failed to produce valid structured output. Raw output: {result.raw}",
                    "is_new_project": False,
                    "taskmaster_error": "Invalid JSON output from task"
                }
        else:
            # Handle cases where the task execution failed or produced no raw output
            # (e.g., if task failed after retries, result might not have .raw or be None)
            print("Taskmaster task failed or produced no output.")
            return {
                "project_name": "error_taskmaster_failed",
                "refined_brief": "Taskmaster task execution failed or yielded no output.",
                "is_new_project": False,
                "taskmaster_error": "Task execution failed or no output"
            }

    def execute_pipeline(self, initial_inputs: dict):
        current_artifacts = {}
        start_index = 0
        stages = [
            "taskmaster", "architecture", "crew_assignment",
            "subagent_execution", "final_assembly"
        ]

        if self.state is None: # Project name to be determined by Taskmaster
            print("Orchestrator state not initialized, running Taskmaster first...")
            taskmaster_output = self.run_taskmaster_workflow(initial_inputs)

            actual_project_name = taskmaster_output.get("project_name")
            if not actual_project_name or "error_" in actual_project_name:
                print(f"Error: Taskmaster failed to provide a valid project name. Output: {taskmaster_output}")
                # Attempt to log this critical failure if possible, though state isn't fully up.
                # For now, just return the error output from taskmaster.
                return {"error": "Taskmaster failed to initialize project", "details": taskmaster_output}

            print(f"Taskmaster determined project name: {actual_project_name}")
            self.state = ProjectStateManager(actual_project_name)

            # Store Taskmaster's output as the first artifact
            self.state.start_stage("taskmaster") # Mark as started
            self.state.complete_stage("taskmaster", artifacts=taskmaster_output)
            current_artifacts["taskmaster"] = taskmaster_output

            # Update initial_inputs with the determined project name for subsequent stages
            initial_inputs["project_name"] = actual_project_name

            # Taskmaster stage is done, so next stage is architecture
            start_index = stages.index("architecture")
        else:
            # State was initialized, meaning project_name was provided (resuming or specific project run)
            # Add project_name to initial_inputs if not already present from the state
            if "project_name" not in initial_inputs and hasattr(self.state, 'project_info'):
                 initial_inputs["project_name"] = self.state.project_info.get("name", self.initial_project_name_hint)

            current_artifacts = self.state.get_artifacts()
            resume_point = self.state.resume_point()

            if resume_point is None and self.state.state.get("status") == "completed":
                print("Project already completed.")
                self.state.get_summary().print()
                return self.state.get_artifacts()

            if resume_point is None and self.state.state.get("status") != "failed":
                if self.state.state.get("status") != "completed":
                    print("All stages completed. Finalizing project...")
                    self.state.finalize_project()
                self.state.get_summary().print()
                return self.state.get_artifacts()

            print(f"Resuming project '{initial_inputs['project_name']}' at stage: {resume_point if resume_point else 'start'}")

            if resume_point:
                try:
                    start_index = stages.index(resume_point)
                except ValueError:
                    print(f"Error: Resume point '{resume_point}' not found in defined stages. Defaulting to start.")
                    self.state.fail_stage("orchestrator_setup", f"Invalid resume point: {resume_point}")
                    # This error should ideally be handled more gracefully, maybe by returning artifacts or error.
                    # For now, it might try to run from start_index = 0 if not caught by fail_stage.
                    # To be safe, let's print summary and return if resume_point is invalid.
                    self.state.get_summary().print()
                    return self.state.get_artifacts()


        # Main execution loop for stages
        for i in range(start_index, len(stages)):
            stage = stages[i]

            # This check is vital: if taskmaster was run above, it's already completed.
            if self.state.is_completed(stage):
                print(f"Stage {stage} already completed. Skipping.")
                # Ensure its artifacts are in current_artifacts if not already loaded by get_artifacts()
                if stage not in current_artifacts and self.state.get_artifacts(stage):
                    current_artifacts[stage] = self.state.get_artifacts(stage)
                continue

            self.state.start_stage(stage)

            try:
                inputs_for_stage = {**initial_inputs, **current_artifacts}

                # Ensure project_name is in inputs_for_stage from self.state if available
                if "project_name" not in inputs_for_stage and self.state.project_info:
                    inputs_for_stage["project_name"] = self.state.project_info.get("name")


                print(f"\nStarting {stage} stage for project '{inputs_for_stage.get('project_name', 'N/A')}'...")
                result = self.workflows[stage](inputs_for_stage)

                self.state.complete_stage(stage, artifacts=result)
                if result:
                    current_artifacts[stage] = result
                print(f"Completed {stage} stage successfully.")

            except Exception as e:
                error_msg = f"Stage {stage} failed: {str(e)}"
                self.state.fail_stage(stage, error_msg)
                print(error_msg)
                import traceback
                traceback.print_exc()
                break

        # Finalize project if all stages completed successfully
        if self.state.state["status"] != "failed":
            all_stages_done = all(self.state.is_completed(s) for s in stages)
            if all_stages_done:
                self.state.finalize_project()
                print("Project completed and finalized successfully.")
            else:
                print("Workflow execution finished, but not all stages were completed. Project not finalized.")

        if self.state: # Ensure state is initialized before printing summary
            self.state.get_summary().print()
            return self.state.get_artifacts()
        else: # Should not happen if taskmaster ran correctly
            print("Error: Orchestrator state was not initialized.")
            return {"error": "Orchestrator state not initialized."}
