import json
import logging
# Removed direct crewai imports like Process, Task, ValidatedCrew if they are not used directly
# by this simplified flow. The agents it might use would be pre-configured.

# Assuming agents are imported if this flow directly uses them for its internal logic.
# For this refactoring, we'll assume the "existing architecture workflow logic"
# is a black box that produces the artifacts.
# If that black box itself uses agents and tasks, those would remain.

from ..project_manager import ProjectStateManager # Added

# Placeholder for the actual core logic of generating architecture.
# This function would contain the "existing architecture workflow logic".
def _perform_architecture_generation(inputs: dict):
    # This is where the original complex logic of idea_to_architecture_flow would go.
    # For example, running internal crews, calling agents, etc.
    # It should return a dictionary of artifacts like:
    # {
    #     "architecture_doc": "...",
    #     "technology_stack": ["...", "..."],
    #     "system_diagrams": {"diag1_url": "...", "diag2_url": "..."}
    # }
    print("Performing internal architecture generation logic...")
    # Simulate artifact creation based on inputs
    architecture_doc = f"Architecture document for {inputs.get('project_name', 'Unknown Project')} based on user idea: {inputs.get('user_idea', inputs.get('taskmaster', {}).get('initial_brief', 'No user idea provided'))}"
    tech_stack = ["Python", "FastAPI", "React", "PostgreSQL"]
    diagrams = {"conceptual_diagram": "path/to/conceptual.png", "component_diagram": "path/to/component.png"}

    # Simulate some processing based on other inputs
    if inputs.get("stakeholder_feedback"):
        architecture_doc += f"\nIncorporating feedback: {inputs['stakeholder_feedback']}"
    if inputs.get("market_research_data"):
        tech_stack.append("Elasticsearch for search capabilities based on market research.")
    if inputs.get("constraints"):
        architecture_doc += f"\nConsidering constraints: {inputs['constraints']}"
    if inputs.get("technical_vision"):
         architecture_doc += f"\nAligned with technical vision: {inputs['technical_vision']}"

    return {
        "architecture_doc": architecture_doc,
        "technology_stack": tech_stack,
        "system_diagrams": diagrams,
        "notes": "This is a simplified mock output from _perform_architecture_generation."
    }

def run_idea_to_architecture_workflow(inputs: dict):
    project_name = inputs.get("project_name")
    if not project_name:
        # Fallback or raise error if project_name is critical and not found
        # For now, let's try to get it from a potential taskmaster artifact if this flow
        # expects to run after a taskmaster stage that might not explicitly pass project_name.
        # However, the new orchestrator should be passing project_name in initial_inputs.
        print("Warning: project_name not found directly in inputs for idea_to_architecture_flow.")
        # Attempt to find it in a common artifact location if this is a sub-flow context
        project_name = inputs.get("taskmaster", {}).get("project_name", "default_project_temp_name")
        if project_name == "default_project_temp_name":
             print("Critical Error: Project name could not be determined for state management in architecture flow.")
             raise ValueError("Project name is required for ProjectStateManager in idea_to_architecture_flow")

    state = ProjectStateManager(project_name) # Initialize with project_name

    # Check if we have existing artifacts for the "architecture" stage
    # The orchestrator already checks this, but an internal check can be a safeguard
    # or useful if this flow is ever called directly.
    # However, to align with the issue's Orchestrator which calls this for an active stage,
    # we might assume this check is optional here if orchestrator guarantees stage is active.
    # For robustness, let's keep it, especially if this flow could be resumed internally.
    # The issue example shows this check.
    if state.is_completed("architecture"):
        print(f"'{project_name}': Using cached architecture artifacts for stage 'architecture'")
        return state.get_artifacts("architecture")

    print(f"'{project_name}': Running main logic for 'architecture' stage.")
    try:
        # ... existing architecture workflow logic ...
        # This is now encapsulated in _perform_architecture_generation
        # The 'inputs' dictionary here is what the orchestrator provides,
        # which includes initial_inputs and all previously collected artifacts.

        # The 'user_idea' key is expected by the original task_interpret_idea.
        # If 'taskmaster' stage ran, its output might be under inputs['taskmaster']
        # Let's ensure the core logic gets what it needs.
        # For example, if taskmaster produced a brief:
        # core_logic_inputs = {**inputs, "user_idea": inputs.get("taskmaster", {}).get("initial_brief")}

        generated_artifacts = _perform_architecture_generation(inputs)

        # The 'artifacts' dictionary should match what's expected by later stages
        # or what needs to be stored for this stage.
        # The issue example returns the artifacts directly. The orchestrator handles calling complete_stage.

        print(f"'{project_name}': Architecture stage completed successfully. Returning artifacts.")
        return generated_artifacts # Orchestrator will call state.complete_stage with this

    except Exception as e:
        print(f"'{project_name}': Error during architecture stage: {str(e)}")
        # Log failure with the state manager. Orchestrator will also catch and log.
        state.fail_stage("architecture", f"Error in run_idea_to_architecture_workflow: {str(e)}")
        raise # Re-raise for the orchestrator to handle
