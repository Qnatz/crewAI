import json
import os # Added for os.path.join, os.makedirs, etc.
from typing import Any, Optional
from crewai import Crew, Task
from crewai.tasks.task_output import TaskOutput
# from ..orchestrators.idea_interpreter_agent.agent import idea_interpreter_agent # Removed
# from .idea_to_architecture_flow import run_idea_to_architecture_flow # Moved to __init__
from .crew_lead_workflow import run_crew_lead_workflow
from .subagent_execution_workflow import run_subagent_execution_workflow
from .final_assembly_workflow import run_final_assembly_workflow
from .tech_vetting_flow import run_tech_vetting_workflow # Added import
from ..project_manager import ProjectStateManager
from ..utils import RichProjectReporter # Added import

# Guardrail function for Taskmaster output
def validate_taskmaster_output(task_output: TaskOutput) -> tuple[bool, Any]: # Changed signature
    if not hasattr(task_output, 'raw') or not isinstance(task_output.raw, str):
        return False, "Guardrail input (task_output.raw) must be a string and present."
    output_str = task_output.raw # Added
    try:
        data = json.loads(output_str) # Changed to output_str
        if not isinstance(data, dict):
            return False, "Output must be a JSON dictionary."
        # Added "project_scope" to required keys
        required_keys = ["project_name", "refined_brief", "is_new_project", "recommended_next_stage", "project_scope"]
        for key in required_keys:
            if key not in data:
                return False, f"Missing key in output: {key}"
        if not isinstance(data["project_name"], str) or not data["project_name"].strip():
            return False, "project_name must be a non-empty string."
        if not isinstance(data["refined_brief"], str) or not data["refined_brief"].strip():
            return False, "refined_brief must be a non-empty string."
        if not isinstance(data["is_new_project"], bool):
            return False, "is_new_project must be a boolean."
        if not isinstance(data["recommended_next_stage"], str) or not data["recommended_next_stage"].strip():
            return False, "recommended_next_stage must be a non-empty string."
        if not isinstance(data["project_scope"], str) or not data["project_scope"].strip(): # Validate project_scope
            return False, "project_scope must be a non-empty string."

        # Optional: Validate project_scope against a list of known scopes
        known_scopes = ["web-only", "mobile-only", "backend-only", "full-stack", "documentation-only", "unknown"]
        if data["project_scope"] not in known_scopes:
            # Allow unknown, but strict validation can be enabled if needed by removing "unknown" or raising error.
            print(f"Warning: Taskmaster output 'project_scope' ('{data['project_scope']}') is not in known scopes: {known_scopes}. Proceeding with the provided scope.")
            # return False, f"project_scope must be one of {known_scopes}."

        return True, data # Return parsed data on success
    except json.JSONDecodeError:
        return False, "Output must be valid JSON." # output_str is not directly visible here, but implied
    except Exception as e:
        return False, f"Validation error: {str(e)}"

class WorkflowOrchestrator:
    ALL_PIPELINE_STAGES = [
        "taskmaster",
        "tech_vetting",
        "architecture",
        "crew_assignment",
        "subagent_execution",
        "final_assembly",
        "persist_generated_code", # New stage
        "project_finalization" # Ensure this is marked by ProjectStateManager
    ]

    def __init__(self, project_name: str = None):
        self.initial_project_name_hint = project_name
        if project_name:
            self.state = ProjectStateManager(project_name)
        else:
            self.state = None # Will be initialized after taskmaster runs

        # Import moved here to attempt to resolve circular dependency
        from .idea_to_architecture_flow import run_idea_to_architecture_flow

        # The workflow functions themselves are expected to handle their inputs
        # and interact with ProjectStateManager if they need to load/save intermediate artifacts
        # specific to their internal steps, or check if they can be skipped.
        self.workflows = {
            "taskmaster": self.run_taskmaster_workflow,
            "tech_vetting": run_tech_vetting_workflow, # Added tech_vetting
            "architecture": run_idea_to_architecture_flow,
            "crew_assignment": run_crew_lead_workflow,
            "subagent_execution": run_subagent_execution_workflow,
            "final_assembly": run_final_assembly_workflow,
            "persist_generated_code": self.run_persist_code_files_workflow # Added new workflow
        }

    def run_persist_code_files_workflow(self, inputs: dict):
        print(f"DEBUG: Entering run_persist_code_files_workflow for project '{self.state.project_info.get('name', 'N/A')}'")
        if not self.state or not self.state.project_info:
            error_msg = "Error: Project state or project_info not initialized in persist_code_files_workflow."
            print(error_msg)
            return {"status": "error", "message": error_msg, "files_written": []}

        project_path = self.state.project_info.get('path')
        if not project_path:
            error_msg = "Error: Project path not found in project_info."
            print(error_msg)
            return {"status": "error", "message": error_msg, "files_written": []}

        final_assembly_artifacts = inputs.get("final_assembly", {})
        if not isinstance(final_assembly_artifacts, dict): # Check if it's a dict
            error_msg = f"Error: final_assembly artifacts are not in the expected dictionary format. Found: {type(final_assembly_artifacts)}"
            print(error_msg)
            # Try to access .raw if it's a TaskOutput object, as a common case
            if hasattr(final_assembly_artifacts, 'raw') and isinstance(final_assembly_artifacts.raw, dict):
                print("DEBUG: Attempting to use .raw attribute from final_assembly_artifacts.")
                final_assembly_artifacts = final_assembly_artifacts.raw
            else:
                return {"status": "error", "message": error_msg, "files_written": []}


        generated_files_dict = final_assembly_artifacts.get("generated_files", {})
        if not generated_files_dict:
            print("Info: No 'generated_files' found in final_assembly_artifacts or it's empty. No files to persist.")
            return {"status": "success", "message": "No files to persist.", "files_written": [], "output_path": project_path}

        if not isinstance(generated_files_dict, dict):
            error_msg = f"Error: 'generated_files' is not a dictionary. Found: {type(generated_files_dict)}"
            print(error_msg)
            return {"status": "error", "message": error_msg, "files_written": []}

        files_written_paths = []
        errors_encountered = []

        print(f"Persisting {len(generated_files_dict)} generated file(s) to path: {project_path}")
        for file_path_in_manifest, code_content in generated_files_dict.items():
            if not isinstance(file_path_in_manifest, str) or not file_path_in_manifest.strip():
                print(f"Warning: Invalid file_path_in_manifest (empty or not a string): '{file_path_in_manifest}'. Skipping.")
                errors_encountered.append(f"Invalid file path: {file_path_in_manifest}")
                continue

            if not isinstance(code_content, str):
                if code_content is not None:
                    print(f"Warning: Code content for '{file_path_in_manifest}' is not a string (type: {type(code_content)}). Will attempt to write as str().")
                code_content = str(code_content) if code_content is not None else ""


            try:
                sanitized_relative_path = os.path.normpath(file_path_in_manifest.lstrip('/\\'))
                if ".." in sanitized_relative_path.split(os.path.sep):
                    print(f"Error: Invalid file path '{file_path_in_manifest}' contains '..'. Skipping for security.")
                    errors_encountered.append(f"Path traversal attempt: {file_path_in_manifest}")
                    continue

                target_file_path = os.path.join(project_path, sanitized_relative_path)

                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

                with open(target_file_path, "w", encoding="utf-8") as f:
                    f.write(code_content)
                files_written_paths.append(sanitized_relative_path)
                print(f"Successfully wrote: {target_file_path}")
            except Exception as e:
                error_msg = f"Error writing file '{file_path_in_manifest}' to '{target_file_path}': {e}"
                print(error_msg)
                errors_encountered.append(error_msg)

        if errors_encountered:
            return {
                "status": "partial_success",
                "message": "Completed persisting files, but some errors were encountered.",
                "files_written": files_written_paths,
                "errors": errors_encountered,
                "output_path": project_path
            }

        return {
            "status": "success",
            "message": "All generated files persisted successfully.",
            "files_written": files_written_paths,
            "output_path": project_path
        }

    # run_idea_interpretation_workflow method will be deleted by removing all its lines.
    # The diff will show this as a deletion of the block.

    def run_taskmaster_workflow(self, inputs: dict):
        print("Executing Taskmaster workflow...")
        from ..taskmaster.taskmaster_agent import taskmaster_agent
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
                "is_new_project": False,
                "recommended_next_stage": "architecture",
                "project_scope": "unknown", # Default fallback
                "taskmaster_error": "No user_request provided"
            }

        taskmaster_task = Task(
            description=f"Process the following user request: '{user_request}'. "
                        f"Determine if this pertains to a new or existing project. "
                        f"If it's a new project, generate a unique and descriptive project name (e.g., based on key themes from the request, and ensure it's filesystem-safe). "
                        f"Then, create a refined project brief based on the request. "
                        f"You MUST use the 'knowledge_base_tool_instance' to check for existing projects or ideas if applicable. "
                        f"Focus on understanding the core needs and deliverables. "
                        f"Based on the project's nature (e.g., complexity, use of new/unproven technologies, high uncertainty), recommend the next logical stage. "
                        f"Valid recommendations are: 'tech_vetting' (if new/complex tech evaluation is needed) or 'architecture' (if project can proceed to design). "
                        f"Also, determine the primary scope of the project from the following options: 'web-only', 'mobile-only', 'backend-only', 'full-stack', 'documentation-only'. If ambiguous or not fitting these, use 'unknown'. "
                        "Your final response MUST be ONLY a single, valid JSON object that strictly adheres to the structure specified in the expected_output. Do not include any other text, explanations, or conversational remarks before or after the JSON object.",
            agent=taskmaster_agent,
            expected_output="A JSON object containing: "
                            "'project_name' (string, unique and descriptive for new projects), "
                            "'refined_brief' (string, a concise summary and scope), "
                            "'is_new_project' (boolean, True if this is identified as a new project, False otherwise), "
                            "'recommended_next_stage' (string, either 'tech_vetting' or 'architecture'), "
                            "and 'project_scope' (string, one of 'web-only', 'mobile-only', 'backend-only', 'full-stack', 'documentation-only', 'unknown').",
            guardrail=validate_taskmaster_output,
            max_retries=1 # Keep retries low for faster failure if guardrail fails
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
                    "recommended_next_stage": "architecture",
                    "project_scope": "unknown", # Default fallback
                    "taskmaster_error": "Invalid JSON output from task"
                }
        else:
            # Handle cases where the task execution failed or produced no raw output
            print("Taskmaster task failed or produced no output.")
            return {
                "project_name": "error_taskmaster_failed",
                "refined_brief": "Taskmaster task execution failed or yielded no output.",
                "is_new_project": False,
                "recommended_next_stage": "architecture",
                "project_scope": "unknown", # Default fallback
                "taskmaster_error": "Task execution failed or no output"
            }

    def execute_pipeline(self, initial_inputs: dict, mock_taskmaster_output: Optional[dict] = None):
        current_artifacts = {}

        # Define the full sequence of possible stages
        defined_pipeline_stages = [
            "taskmaster",
            "tech_vetting",
            "architecture",
            "crew_assignment",
            "subagent_execution",
            "final_assembly",
            "persist_generated_code" # New stage
        ]

        stages_to_run = []
        next_stage_index = 0

        if mock_taskmaster_output and self.state is None:
            print("DEBUG: Using MOCKED Taskmaster output.")
            taskmaster_output = mock_taskmaster_output
            current_artifacts["taskmaster"] = taskmaster_output
            # Initialize self.state here using project_name from mock_taskmaster_output
            actual_project_name = taskmaster_output.get("project_name")
            if not actual_project_name or not isinstance(actual_project_name, str):
                print("ERROR: Mocked Taskmaster output missing or invalid 'project_name'. Cannot proceed.")
                # Return an error structure or raise an exception
                return {"error": "Mocked Taskmaster output missing or invalid project_name"}
            self.state = ProjectStateManager(actual_project_name)
            self.state.start_stage("taskmaster") # Mark as started
            self.state.complete_stage("taskmaster", artifacts=taskmaster_output) # Mark as completed with mock data
            initial_inputs["project_name"] = actual_project_name # Update initial_inputs for subsequent stages
            # Determine stages_to_run based on mock_taskmaster_output
            recommended_next = taskmaster_output.get("recommended_next_stage", "architecture")
            stages_to_run.append("taskmaster") # Mocked taskmaster is considered 'done'
            if recommended_next == "tech_vetting":
              stages_to_run.extend(["tech_vetting", "architecture", "crew_assignment", "subagent_execution", "final_assembly"])
            elif recommended_next == "architecture":
              stages_to_run.extend(["architecture", "crew_assignment", "subagent_execution", "final_assembly"])
            else:
              print(f"Warning: Unknown recommended next stage '{recommended_next}' in mock. Defaulting to architecture flow.")
              stages_to_run.extend(["architecture", "crew_assignment", "subagent_execution", "final_assembly"])
            next_stage_index = 0 # Start iterating from the beginning of stages_to_run (it will skip 'taskmaster')
        elif self.state is None: # Original block for when state is None (New Project) and no mock
            print("Orchestrator state not initialized, running actual Taskmaster workflow...")
            taskmaster_output = self.run_taskmaster_workflow(initial_inputs)
            current_artifacts["taskmaster"] = taskmaster_output

            if "taskmaster_error" in taskmaster_output or "error_" in taskmaster_output.get("project_name", ""):
                print(f"Error: Taskmaster failed. Output: {taskmaster_output}")
                # Potentially create a minimal state for error reporting if project_name is usable
                error_project_name = taskmaster_output.get("project_name", "taskmaster_failed_project")
                if "error_" in error_project_name: error_project_name = "taskmaster_failed_project" # Ensure valid name
                self.state = ProjectStateManager(error_project_name)
                self.state.fail_stage("taskmaster", taskmaster_output.get("refined_brief", "Taskmaster critical failure"))
                # No further stages will run. Report will be generated at the end.
                stages_to_run = [] # Empty list, skip loop
            else:
                actual_project_name = taskmaster_output.get("project_name")
                print(f"Taskmaster determined project name: {actual_project_name}")
                self.state = ProjectStateManager(actual_project_name)
                self.state.start_stage("taskmaster")
                self.state.complete_stage("taskmaster", artifacts=taskmaster_output)
                initial_inputs["project_name"] = actual_project_name # Update for subsequent stages

                # Determine the actual sequence of stages based on Taskmaster's recommendation
                recommended_next = taskmaster_output.get("recommended_next_stage", "architecture")
                print(f"Taskmaster recommended next stage: {recommended_next}")

                stages_to_run.append("taskmaster") # Already effectively done for new projects
                if recommended_next == "tech_vetting":
                    stages_to_run.extend(["tech_vetting", "architecture", "crew_assignment", "subagent_execution", "final_assembly"])
                elif recommended_next == "architecture":
                    stages_to_run.extend(["architecture", "crew_assignment", "subagent_execution", "final_assembly"])
                else: # Default to architecture if recommendation is unclear
                    print(f"Warning: Unknown recommended next stage '{recommended_next}'. Defaulting to architecture flow.")
                    stages_to_run.extend(["architecture", "crew_assignment", "subagent_execution", "final_assembly"])

                # Since taskmaster is "done" by this block, the loop should start from the next stage.
                # We mark taskmaster as completed, and the loop will skip it.
                next_stage_index = 0 # The loop will check is_completed for taskmaster

        else: # Resuming an existing project
            if "project_name" not in initial_inputs and hasattr(self.state, 'project_info'):
                 initial_inputs["project_name"] = self.state.project_info.get("name", self.initial_project_name_hint)
            print(f"Resuming existing project: {initial_inputs.get('project_name', 'Unknown')}")
            current_artifacts = self.state.get_artifacts() # Load all existing artifacts

            resume_point = self.state.resume_point()
            if resume_point is None and self.state.state.get("status") == "completed":
                print("Project already completed.")
                # Report will be generated at the end.
                stages_to_run = [] # Skip loop
            elif resume_point is None and self.state.state.get("status") != "failed":
                 if self.state.state.get("status") != "completed": # Should have been caught by finalize_project
                    print("All stages completed. Finalizing project...")
                    self.state.finalize_project()
                 stages_to_run = [] # Skip loop
            elif resume_point:
                print(f"Resuming at stage: {resume_point}")
                # Determine the sequence of stages from the resume point.
                # This needs to consider the original recommended path if stored, or assume full path.
                # For simplicity now, assume the defined_pipeline_stages is the path.
                try:
                    resume_idx = defined_pipeline_stages.index(resume_point)
                    stages_to_run = defined_pipeline_stages # Run all stages from the full list
                    next_stage_index = resume_idx # Start loop from this index
                except ValueError:
                    print(f"Error: Resume point '{resume_point}' not found in defined stages. Cannot resume.")
                    self.state.fail_stage("orchestrator_resume", f"Invalid resume point: {resume_point}")
                    stages_to_run = [] # Skip loop
            else: # No resume point, project not completed or failed (e.g. just initialized but no stages run)
                # This case might indicate needing to run taskmaster again or re-evaluate.
                # For now, assume it means start from the beginning of a standard flow.
                # This path needs careful consideration if Taskmaster's recommendation isn't persisted.
                # Let's assume if we are here, it's like a new project that somehow has state.
                # Fallback: attempt to run a default sequence.
                # However, if taskmaster output is in artifacts, we can use its recommendation.
                taskmaster_output = current_artifacts.get("taskmaster", {})
                recommended_next = taskmaster_output.get("recommended_next_stage", "architecture")
                print(f"No clear resume point, using Taskmaster recommendation ('{recommended_next}') or default flow.")
                if recommended_next == "tech_vetting" and not self.state.is_completed("tech_vetting"):
                    stages_to_run = defined_pipeline_stages
                elif recommended_next == "architecture" and not self.state.is_completed("architecture"):
                     stages_to_run = [s for s in defined_pipeline_stages if s != "tech_vetting"]
                else: # Default or if recommended stage is already done, try full sequence
                    stages_to_run = defined_pipeline_stages
                next_stage_index = 0


        # Main execution loop
        for i in range(next_stage_index, len(stages_to_run)):
            stage = stages_to_run[i]

            if self.state.is_completed(stage):
                print(f"Stage '{stage}' already completed. Skipping.")
                if stage not in current_artifacts and self.state.get_artifacts(stage): # Ensure artifacts are loaded
                    current_artifacts[stage] = self.state.get_artifacts(stage)
                continue

            if stage not in self.workflows:
                print(f"Warning: Stage '{stage}' is defined in the run sequence but no corresponding workflow method exists. Skipping.")
                self.state.fail_stage(stage, f"Workflow for stage '{stage}' not found.") # Log as failure for this stage
                break # Stop pipeline execution if a stage is missing its method

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

        # Finalize project if all prerequisite stages completed successfully
        if self.state.state["status"] != "failed":
            # Define prerequisite stages as all stages in ALL_PIPELINE_STAGES except "project_finalization"
            prerequisite_stages_for_finalization = [s for s in self.ALL_PIPELINE_STAGES if s != "project_finalization"]

            all_prerequisites_done = all(self.state.is_completed(s) for s in prerequisite_stages_for_finalization)

            if all_prerequisites_done:
                # If project status is already 'completed', it implies finalize_project was likely called before
                # (e.g. in a resumed run that found all prerequisites done).
                if self.state.state.get("status") != "completed":
                    print("All prerequisite stages are complete. Finalizing project...")
                    self.state.finalize_project() # This will internally mark 'project_finalization' as complete
                else:
                    # This case implies all prerequisites are done AND project status is 'completed'.
                    # This means 'project_finalization' stage should also be complete.
                    if not self.state.is_completed("project_finalization"):
                        # This would be an inconsistent state: project is "completed" but "project_finalization" stage isn't.
                        # Call finalize_project() again to ensure the stage is marked.
                        print("Project status is 'completed' but 'project_finalization' stage was not marked. Re-finalizing...")
                        self.state.finalize_project()
                    else:
                        print("Project already marked as completed and all prerequisite stages (including finalization) are done.")
            else:
                print("Workflow execution finished, but not all prerequisite stages were completed. Project not finalized by orchestrator.")

        if self.state: # Ensure state is initialized before printing summary
            # self.state.get_summary().print() # Replaced by RichProjectReporter
            reporter = RichProjectReporter(self.state.state) # Pass the state dictionary
            reporter.print_report()
            return self.state.get_artifacts() # Still return artifacts
        else: # Should not happen if taskmaster ran correctly
            print("Error: Orchestrator state was not initialized.")
            return {"error": "Orchestrator state not initialized."}
