import sys
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, InvalidResponse # Added InvalidResponse
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

    project_name_for_orchestrator = None
    pipeline_inputs = {}

    listed_projects = ProjectStateManager.list_projects()

    if listed_projects:
        console.print(Panel(Text("Select a project to resume or start a new one.", style="bold green"), title="[bold cyan]Project Selection[/bold cyan]", border_style="green"))
        for i, proj in enumerate(listed_projects):
            # Base display string with rich_name and last_updated
            display_text = Text(f"{i+1}. ")
            # Use Text.from_markup if rich_name might contain Rich Console Markup, otherwise Text() is fine.
            # Given ✅ and ❌ are simple characters, Text() is okay, but from_markup is safer if it evolves.
            display_text.append(Text.from_markup(proj['rich_name']))
            display_text.append(Text(f" - Last updated: {proj['last_updated']}", style="dim")) # Using dim style

            console.print(display_text)

            # If the project failed and has an error message, display it
            if proj['status'] == 'failed' and proj.get('error_message'):
                error_text = Text(f"   Error: {proj['error_message']}", style="italic red")
                console.print(error_text)

        new_project_option_num = len(listed_projects) + 1
        console.print(Text(f"{new_project_option_num}. Start New Project", style="bold yellow"))

        choice_prompt = f"Enter project number (1-{len(listed_projects)}) to resume, or '{new_project_option_num}' (or 'n') for a new project"

        while True:
            try:
                raw_choice = Prompt.ask(choice_prompt).strip().lower()
                if raw_choice == 'n' or raw_choice == str(new_project_option_num):
                    user_idea = Prompt.ask("[bold yellow]Please enter your new project idea or request[/bold yellow]")
                    pipeline_inputs = {"user_request": user_idea}
                    project_name_for_orchestrator = None # Taskmaster will handle naming for new projects
                    console.print("Starting a new project...")
                    break

                chosen_idx = int(raw_choice) - 1
                if 0 <= chosen_idx < len(listed_projects):
                    chosen_project = listed_projects[chosen_idx]
                    project_name_for_orchestrator = chosen_project['name'] # Use name to load project state
                    # For resuming, pipeline_inputs might not need 'user_request' initially if orchestrator handles resume logic
                    # pipeline_inputs = {"project_name": project_name_for_orchestrator}
                    # The orchestrator's __init__ takes project_name, so this is enough.
                    # execute_pipeline might need specific inputs if resuming a particular stage,
                    # but for now, just loading the project is the primary goal.
                    # If Taskmaster is the first stage for resume, it might need a way to know it's a resume.
                    # For now, let's assume the orchestrator handles this via project_name.
                    # The 'pipeline_inputs' for a resumed project might be different or even empty if the orchestrator
                    # just picks up from the saved state.
                    # For now, let's set it to indicate a resume if needed by later stages.
                    pipeline_inputs = {"project_name": project_name_for_orchestrator, "action": "resume"}
                    console.print(f"Resuming project: [bold cyan]{project_name_for_orchestrator}[/bold cyan]")
                    break
                else:
                    console.print(f"[bold red]Invalid selection. Please choose a number between 1 and {new_project_option_num} or 'n'.[/bold red]")
            except ValueError:
                console.print("[bold red]Invalid input. Please enter a number or 'n'.[/bold red]")
            except InvalidResponse: # Should not happen with basic Prompt.ask, but good practice
                console.print("[bold red]Invalid response received from prompt.[/bold red]")
    else:
        console.print(Panel(Text("No existing projects found.", style="italic"), title="[bold cyan]Project Status[/bold cyan]", border_style="yellow"))
        user_idea = Prompt.ask("[bold yellow]Please enter your new project idea or request[/bold yellow]")
        pipeline_inputs = {"user_request": user_idea}
        project_name_for_orchestrator = None

    # --- Execute Pipeline ---
    # Pass project_name_for_orchestrator to WorkflowOrchestrator constructor
    # This allows it to load the project state if a project name is provided.
    # For mocked run, project_name_for_orchestrator is None, so orchestrator.state will be None initially.
    orchestrator = WorkflowOrchestrator(project_name=project_name_for_orchestrator)
    try:
        # pipeline_inputs now contains the user's request.
        # The mock_taskmaster_output is removed as Taskmaster will run live.
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
