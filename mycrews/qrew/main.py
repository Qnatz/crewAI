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
from .llm_config import default_llm
from . import config as crew_config

# TaskMasterAgent import is removed as it's handled by the orchestrator's "taskmaster" stage
# from .taskmaster import taskmaster_agent

os.environ["LITELLM_DEBUG"] = "0" # Disabled debug for cleaner output, can be "1"

from .workflows.orchestrator import WorkflowOrchestrator
from .project_manager import ProjectStateManager # Added import

def run_qrew():
    print("Initializing Qrew System...")

    # --- Project Setup ---
    # project_name = "FitnessTrackerApp" # Example project name - This is now determined by Taskmaster
    # print(f"\nStarting/Resuming project: {project_name}") # Moved to after orchestrator run

    # State manager is now primarily managed by the orchestrator.
    # Pre-run checks for resume point are removed as project name isn't known yet.
    # temp_state_manager_for_info = ProjectStateManager(project_name)
    # resume_point_check = temp_state_manager_for_info.resume_point()
    # project_path = temp_state_manager_for_info.project_info["path"] # Get project path for saving final output

    # if temp_state_manager_for_info.state.get("status") == "completed":
    #     print(f"Project '{project_name}' is already marked as completed.")
    # elif resume_point_check:
    #     print(f"Resuming existing project at stage: {resume_point_check}")
    # else:
    #     print(f"Project status: {temp_state_manager_for_info.state.get('status')}. Orchestrator will determine next steps.")
    print("Project name will be determined by the Taskmaster workflow.")

    # --- Inputs Preparation ---
    sample_user_request = "I need a new mobile app for tracking personal fitness goals. It should be fun and engaging, perhaps with gamification elements and personalized plans. Call it 'FitQuest'."
    sample_project_goal = "Develop a market-leading mobile fitness tracking application."
    sample_priority = "High" # This might be used by taskmaster or other stages

    # These were previously passed to taskmaster, now part of initial inputs for the orchestrator
    # The 'taskmaster' stage in the orchestrator will handle this.
    # taskmaster_result will be an artifact produced by the "taskmaster" stage.

    sample_stakeholder_feedback = "User retention is key. Gamification might be important. Mobile-first approach preferred."
    sample_market_research = "Competitors X and Y lack real-time interaction. Users want personalized training plans."
    sample_project_constraints = "Team has strong Python and React skills. Initial deployment on AWS. Budget for external services is moderate."
    sample_technical_vision = "A modular microservices architecture is preferred for scalability. Prioritize user data privacy."

    pipeline_inputs = {
        # "project_name": project_name, # Removed: Orchestrator will derive this via Taskmaster
        "user_request": sample_user_request,
        "project_goal": sample_project_goal,
        "priority": sample_priority,
        "stakeholder_feedback": sample_stakeholder_feedback,
        "market_research_data": sample_market_research, # Ensure key matches idea_to_architecture
        "constraints": sample_project_constraints,
        "technical_vision": sample_technical_vision
        # 'user_idea' was previously taskmaster_result. The 'architecture' flow expects 'user_idea'.
        # The 'taskmaster' stage in the orchestrator should produce an artifact,
        # which then becomes available for subsequent stages like 'architecture'.
        # The orchestrator now handles passing artifacts.
    }

    print("\nInitiating data pipeline with dynamic project determination...")

    # --- Execute Pipeline ---
    orchestrator = WorkflowOrchestrator() # Initialize without project_name
    try:
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
