import sys
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from collections import OrderedDict # To maintain order for display after processing
# Add the project root (/app) to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')) # Corrected path
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

# Initialize Rich Console
console = Console()

# TaskMasterAgent import is removed as it's handled by the orchestrator's "taskmaster" stage
# from .taskmaster import taskmaster_agent

os.environ["LITELLM_DEBUG"] = "0" # Disabled debug for cleaner output, can be "1"

from .workflows.orchestrator import WorkflowOrchestrator
from .project_manager import ProjectStateManager # Added import

def display_model_initialization_status(title: str, statuses: list[tuple[str, bool]]):
    """Displays the initialization status of unique models in a Rich Panel."""
    if not statuses:
        content = Text("No models to display status for in this category.", style="italic yellow")
    else:
        # Aggregate statuses: if a model key has at least one True, it's True.
        # Using OrderedDict to preserve the order of first appearance, then sorting for final display.
        processed_statuses = OrderedDict()
        for model_key, success_bool in statuses:
            if model_key not in processed_statuses:
                processed_statuses[model_key] = False # Default to False
            if success_bool: # If any attempt is true, mark it as true for that model key
                processed_statuses[model_key] = True

        if not processed_statuses:
             content = Text("No valid model statuses to display after processing.", style="italic yellow")
        else:
            status_texts = []
            # Sort items by model_key for consistent display order
            sorted_model_statuses = sorted(processed_statuses.items())

            for model_key, aggregated_success_bool in sorted_model_statuses:
                # Ensure model_key is a string for Text()
                model_key_str = str(model_key) if model_key is not None else "N/A"
                model_text = Text(f"{model_key_str}: ", style="default")
                if aggregated_success_bool:
                    model_text.append("✅", style="bright_green") # Changed to ✅
                else:
                    model_text.append("❌", style="bright_red")   # Use bright_red
                status_texts.append(model_text)
            content = Text("\n").join(status_texts)

    # Ensure title is Text if it's a string with markup, or already Text
    panel_title = title if isinstance(title, Text) else Text.from_markup(title)
    panel = Panel(content, title=panel_title, border_style="blue", expand=False, padding=(1, 2))
    console.print(panel)

def run_qrew():
    # Display LLM initialization status first using Rich
    display_model_initialization_status("[bold cyan]--- LLM Initialization ---[/bold cyan]", llm_initialization_statuses)

    # Placeholder for TFLite and other models as per requirements, also using Rich
    display_model_initialization_status("[bold cyan]--- TFLite Model Initialization ---[/bold cyan]", [])
    # Example with placeholder models:
    # display_model_initialization_status("[bold cyan]--- Other Model Initialization ---[/bold cyan]", [("Embedding Model", True), ("Another Model", False)])

    # The old "Initializing Qrew System..." print might be redundant or can be styled too.
    # For now, let's keep it or use console.print for consistency if desired.
    # console.print("\n[bold]Initializing Qrew System...[/bold]")
    # Keeping the original print for now, as the focus is on the status boxes.
    print("\nInitializing Qrew System...")

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
    user_request = ""
    project_name_for_orchestrator = None
    pipeline_inputs = {}
    selected_project_state = None

    available_projects = list_available_projects()

    taskmaster_content_texts = []
    if available_projects:
        taskmaster_content_texts.append(Text("Available Projects:", style="bold green"))
        for i, name in enumerate(available_projects):
            taskmaster_content_texts.append(Text(f"  {i+1}. {name}"))
    else:
        taskmaster_content_texts.append(Text("No existing projects found.", style="italic yellow"))

    taskmaster_content_texts.append(Text("\nWrite your new idea or select an existing project number:", style="cyan"))

    combined_content = Text("\n").join(taskmaster_content_texts)

    taskmaster_panel = Panel(
        combined_content,
        title="[bold magenta]Taskmaster Initialization[/bold magenta]",
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(taskmaster_panel)

    # Use Prompt.ask for input, placed after the panel displaying options and prompt instructions.
    user_input_str = Prompt.ask(Text("Your choice", style="bold default"))

    try:
        selected_index = int(user_input_str) - 1
        if 0 <= selected_index < len(available_projects):
            project_name_for_orchestrator = available_projects[selected_index]
            console.print(Text(f"Selected existing project: '{project_name_for_orchestrator}'", style="bold blue"))

            temp_state_manager = ProjectStateManager(project_name_for_orchestrator)
            selected_project_state = temp_state_manager.state

            if selected_project_state.get("status") == "completed":
                console.print(Panel(Text(f"Project '{project_name_for_orchestrator}' is already marked as completed.\nIf you want to re-run or start a new version, please provide a new idea or modify the project name.", style="yellow"), title="[bold red]Project Completed[/bold red]", border_style="red", expand=False))
                return

            user_request = selected_project_state.get("artifacts", {}).get("taskmaster", {}).get("refined_brief", "")
            if not user_request:
                user_request = selected_project_state.get("user_request", f"Continuing project: {project_name_for_orchestrator}") # Fallback

            pipeline_inputs["project_name"] = project_name_for_orchestrator
        else:
            # Invalid number
            console.print(Text(f"Invalid selection '{user_input_str}'. Treating input as a new idea.", style="yellow"))
            project_name_for_orchestrator = None
            user_request = user_input_str # The full input string is the new idea
    except ValueError:
        # Input is not a number, so it's a new idea
        console.print(Text(f"Input '{user_input_str}' treated as a new idea.", style="italic"))
        project_name_for_orchestrator = None
        user_request = user_input_str

    if project_name_for_orchestrator is None:
        console.print(Text(f"\nProcessing as a new project idea: '{user_request}'", style="bold"))
        pipeline_inputs.update({
            "user_request": user_request,
            "project_goal": "To be defined by Taskmaster based on user request.",
            "priority": "Medium",
            "stakeholder_feedback": "To be gathered or assumed standard.",
            "market_research_data": "To be gathered or assumed standard.",
            "constraints": "Standard web technologies, static site unless specified otherwise.",
            "technical_vision": "Clean, maintainable code. Scalable architecture."
        })
    else:
        console.print(Text(f"Preparing to resume project: {project_name_for_orchestrator}", style="bold"))
        taskmaster_artifacts = selected_project_state.get("artifacts", {}).get("taskmaster", {})

        pipeline_inputs.update({
            "user_request": user_request,
            "project_name": project_name_for_orchestrator,
            "project_goal": selected_project_state.get("project_goal", taskmaster_artifacts.get("project_goal", "Resume existing project goals.")),
            "priority": selected_project_state.get("priority", "As per existing project state."),
            "stakeholder_feedback": selected_project_state.get("stakeholder_feedback", taskmaster_artifacts.get("stakeholder_feedback", "N/A - Resuming project")),
            "market_research_data": selected_project_state.get("market_research_data", taskmaster_artifacts.get("market_research_data", "N/A - Resuming project")),
            "constraints": selected_project_state.get("constraints", taskmaster_artifacts.get("constraints", "As per existing project state.")),
            "technical_vision": selected_project_state.get("technical_vision", taskmaster_artifacts.get("technical_vision", "As per existing project state.")),
            "refined_brief": taskmaster_artifacts.get("refined_brief", user_request),
            "is_new_project": False
        })
        if "refined_brief" in pipeline_inputs:
             pipeline_inputs["user_idea"] = pipeline_inputs["refined_brief"]

    # console.print(f"\nInitiating data pipeline. Project hint: {project_name_for_orchestrator if project_name_for_orchestrator else 'New Project'}")
    # console.print(f"User request for pipeline: {pipeline_inputs.get('user_request')}")
    # The above can be made richer later if needed.


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
