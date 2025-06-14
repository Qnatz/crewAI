import sys
import os
import json
# Add the project root (/app) to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Add the project's src directory to sys.path to allow 'from crewai import ...'
project_src_path = os.path.join(project_root, "src")
if project_src_path not in sys.path:
    sys.path.insert(1, project_src_path)

# Ensure the llm_config is loaded first
# We'll import llm_initialization_statuses after modifying llm_config.py
from .llm_config import default_llm, llm_initialization_statuses # Adjusted import
from . import config as crew_config

# TaskMasterAgent import is removed as it's handled by the orchestrator's "taskmaster" stage
# from .taskmaster import taskmaster_agent

os.environ["LITELLM_DEBUG"] = "0" # Disabled debug for cleaner output, can be "1"

from .workflows.orchestrator import WorkflowOrchestrator
from .project_manager import ProjectStateManager # Added import

def display_model_initialization_status(title: str, statuses: list[tuple[str, bool]]):
    """Displays the initialization status of models in a formatted box."""
    print(f"\n{title}")
    if not statuses:
        print("No models to display status for in this category.")
    else:
        for model_name, status in statuses:
            icon = "✔️" if status else "❌"
            print(f"{model_name}: {icon}")
    print("-" * (len(title) if len(title) > 20 else 20)) # Adjust width based on title or min width

def run_qrew():
    # Display LLM initialization status first
    # Note: llm_initialization_statuses is populated when llm_config.py is imported
    display_model_initialization_status("--- LLM Initialization ---", llm_initialization_statuses)

    # Placeholder for TFLite and other models as per requirements
    display_model_initialization_status("--- TFLite Model Initialization ---", [])
    # Example with placeholder models:
    # display_model_initialization_status("--- Other Model Initialization ---", [("Embedding Model", True), ("Another Model", False)])

    print("\nInitializing Qrew System...") # Original print statement

    # --- Helper function to list projects ---
    def list_available_projects():
        projects_dir = os.path.join(project_root, "mycrews", "qrew", "projects")
        if not os.path.isdir(projects_dir):
            return []

        project_folders = []
        for item in os.listdir(projects_dir):
            if os.path.isdir(os.path.join(projects_dir, item)):
                # Attempt to read project name from state.json if it exists
                state_file_path = os.path.join(projects_dir, item, "state.json")
                if os.path.exists(state_file_path):
                    try:
                        with open(state_file_path, 'r') as f:
                            state_data = json.load(f)
                            project_name_from_state = state_data.get("project_name")
                            if project_name_from_state:
                                project_folders.append(project_name_from_state)
                            else:
                                project_folders.append(item) # Fallback to folder name
                    except json.JSONDecodeError:
                        project_folders.append(item) # Fallback if state.json is malformed
                else:
                    project_folders.append(item) # Fallback if no state.json
        return project_folders

    # --- Taskmaster Initialization / User Input ---
    print("\n--- Taskmaster Initialization ---")

    user_request = ""
    project_name_for_orchestrator = None # Will be passed to orchestrator if a project is selected
    pipeline_inputs = {}

    available_projects = list_available_projects()
    if available_projects:
        print("Available Projects:")
        for i, name in enumerate(available_projects):
            print(f"{i + 1}. {name}")
        print("-" * 30) # Separator

    prompt_message = "Write your new idea or select an existing project number (e.g., '1'): "
    user_input_str = input(prompt_message)

    selected_project_state = None # To store loaded state for existing projects

    try:
        selected_index = int(user_input_str) - 1
        if 0 <= selected_index < len(available_projects):
            project_name_for_orchestrator = available_projects[selected_index]
            print(f"Selected existing project: {project_name_for_orchestrator}")

            # Attempt to load state for the selected project
            temp_state_manager = ProjectStateManager(project_name_for_orchestrator)
            selected_project_state = temp_state_manager.state # state is loaded in ProjectStateManager's __init__

            if selected_project_state.get("status") == "completed":
                print(f"Project '{project_name_for_orchestrator}' is already marked as completed.")
                print("If you want to re-run or start a new version, please provide a new idea or modify the project name.")
                # Optionally, exit or loop back to input prompt
                return # Exit run_qrew if project is completed.

            user_request = selected_project_state.get("artifacts", {}).get("taskmaster", {}).get("refined_brief", "")
            if not user_request: # Fallback if refined_brief is not found
                user_request = selected_project_state.get("user_request", f"Continuing project: {project_name_for_orchestrator}") # Original user_request if available

            pipeline_inputs["project_name"] = project_name_for_orchestrator
        else:
            print("Invalid project number. Treating input as a new idea.")
            project_name_for_orchestrator = None # Ensure it's None for new ideas
            user_request = user_input_str
    except ValueError:
        # Input is not a number, so it's a new idea
        print("Input treated as a new idea.")
        project_name_for_orchestrator = None # Ensure it's None for new ideas
        user_request = user_input_str

    # --- Conditional Inputs Preparation ---
    if project_name_for_orchestrator is None: # New Project
        print("Processing as a new project idea.")
        pipeline_inputs.update({
            "user_request": user_request,
            "project_goal": "To be defined by Taskmaster based on user request.",
            "priority": "Medium",
            "stakeholder_feedback": "To be gathered or assumed standard.",
            "market_research_data": "To be gathered or assumed standard.",
            "constraints": "Standard web technologies, static site unless specified otherwise.",
            "technical_vision": "Clean, maintainable code. Scalable architecture."
            # project_name is NOT set here for new projects
        })
    else: # Existing Project Selected
        print(f"Preparing to resume project: {project_name_for_orchestrator}")
        # Use loaded state if available, otherwise use placeholders
        taskmaster_artifacts = selected_project_state.get("artifacts", {}).get("taskmaster", {})

        pipeline_inputs.update({
            "user_request": user_request, # Already set from state or as placeholder
            "project_name": project_name_for_orchestrator, # Already set
            "project_goal": selected_project_state.get("project_goal", taskmaster_artifacts.get("project_goal", "Resume existing project goals.")),
            "priority": selected_project_state.get("priority", "As per existing project state."),
            "stakeholder_feedback": selected_project_state.get("stakeholder_feedback", taskmaster_artifacts.get("stakeholder_feedback", "N/A - Resuming project")),
            "market_research_data": selected_project_state.get("market_research_data", taskmaster_artifacts.get("market_research_data", "N/A - Resuming project")),
            "constraints": selected_project_state.get("constraints", taskmaster_artifacts.get("constraints", "As per existing project state.")),
            "technical_vision": selected_project_state.get("technical_vision", taskmaster_artifacts.get("technical_vision", "As per existing project state.")),
            # Include other artifacts if they are needed by early stages when resuming
            "refined_brief": taskmaster_artifacts.get("refined_brief", user_request), # refined_brief is often key
            "is_new_project": False # Explicitly false for existing projects
        })
        # Add other top-level state items or specific artifacts if needed by orchestrator/stages
        # For example, if 'architecture' stage needs 'user_idea' (which might be refined_brief)
        if "refined_brief" in pipeline_inputs:
             pipeline_inputs["user_idea"] = pipeline_inputs["refined_brief"]


    # --- Old Inputs Preparation (Commented Out) ---

    # --- Old Inputs Preparation (Commented Out) ---
    # sample_user_request = "Create a simple, modern, single-page responsive website for a personal portfolio..."
    # sample_project_goal = "Develop a clean, professional, single-page personal portfolio website..."
    # ... (other sample variables) ...
    # pipeline_inputs = { ... }

    print(f"\nInitiating data pipeline. Project hint: {project_name_for_orchestrator if project_name_for_orchestrator else 'New Project'}")
    print(f"User request for pipeline: {pipeline_inputs.get('user_request')}")


    # --- Execute Pipeline ---
    # Pass project_name_for_orchestrator to WorkflowOrchestrator constructor
    # This allows it to load the project state if a project name is provided.
    orchestrator = WorkflowOrchestrator(project_name=project_name_for_orchestrator)
    try:
        # pipeline_inputs already contains 'project_name' if one was selected,
        # or it doesn't if it's a new idea (Taskmaster will create it).
        results = orchestrator.execute_pipeline(pipeline_inputs)

        # The orchestrator's ProjectStateManager instance holds the final state
        final_state_manager = orchestrator.state

        if not final_state_manager:
            print("Critical Error: Orchestrator state not initialized after pipeline execution.")
            print("Pipeline Results (if any):", json.dumps(results, indent=2))
            # Early exit if state manager is None, means Taskmaster likely failed critically.
            # The orchestrator.execute_pipeline should return error details in 'results' in this case.
            if results and "error" in results:
                 print(f"Taskmaster error details: {results.get('details')}")
            return # Stop further processing

        actual_project_name = final_state_manager.project_info.get("name", "UnknownProject")
        project_path = final_state_manager.project_info.get("path", ".") # Default to current dir if path missing

        print(f"\nProject '{actual_project_name}' Execution Summary:")
        print("===================================================")

        if final_state_manager.state.get("status") == "completed":
            print(f"Project '{actual_project_name}' successfully completed and finalized.")
            final_output_artifact = results.get("final_assembly", {})
            if not final_output_artifact and results:
                final_output_artifact = results

            print("Final Output Artifacts:", json.dumps(final_output_artifact, indent=2))

            output_file_path = os.path.join(project_path, "final_pipeline_output.json")
            try:
                os.makedirs(project_path, exist_ok=True) # Ensure directory exists
                with open(output_file_path, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"All pipeline artifacts saved to: {output_file_path}")
            except OSError as e:
                print(f"Error saving final output file: {e}. Path: {output_file_path}")


        elif final_state_manager.state.get("status") == "failed":
            print(f"Project '{actual_project_name}' execution failed at stage: {final_state_manager.state.get('current_stage')}")
            print("Review the Workflow Summary printed by the orchestrator for error details.")
        else:
            print(f"Project '{actual_project_name}' execution finished with status: {final_state_manager.state.get('status')}. Not all stages may have completed.")

    except Exception as e:
        print(f"\nAn unexpected error occurred during Qrew pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        # Print error summary from orchestrator if available
        if 'orchestrator' in locals() and hasattr(orchestrator, 'state') and orchestrator.state is not None:
            print("\nPartial Workflow Summary (on error):")
            orchestrator.state.get_summary().print()

        print("\nTroubleshooting Tips from main.py:")
        print("------------------------------------")
        # (Error handling tips like API keys can remain here as a general fallback)
        error_str = str(e).lower()
        litellm_model_env = os.environ.get("LITELLM_MODEL", "").lower()
        if "api_key" in error_str or "authentication" in error_str or "permission" in error_str:
            print("- The error suggests an API key issue or authentication failure.")
            # ... (rest of the API key troubleshooting)
        elif "model_not_found" in error_str:
            print(f"- Model '{litellm_model_env}' not found.")
            # ...
        else:
            print("- Ensure LLM configuration is correct.")
        # ...

if __name__ == "__main__":
    run_qrew()
