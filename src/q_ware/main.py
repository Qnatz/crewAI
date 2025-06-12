# --- Main Q-Ware Entrypoint ---
from q_ware.project_crew_factory import create_project_orchestrator # Updated import

def run_examples():
    # Get the orchestrator (TaskmasterAgent by default for now) from the factory
    # project_specs could be loaded from a file, command line, or user input in a real app
    project_specs_example = {"project_name": "AI Chat Platform"}

    print(f"Attempting to create orchestrator with specs: {project_specs_example}")
    orchestrator = create_project_orchestrator(project_specs=project_specs_example)

    if not orchestrator:
        print("Error: Could not create project orchestrator from factory.")
        return

    print(f"Successfully created orchestrator of type: {type(orchestrator).__name__}")

    print("\n--- Orchestrator Example 1: Tech stack recommendation ---")
    tech_stack_context = {
        "constraints": "Budget under $20K, team familiar with TypeScript and Node.js, needs to scale to 10K users, must be GDPR compliant"
    }
    result1 = orchestrator.run( # Use the orchestrator instance from the factory
        prompt="I need a fast and scalable tech stack for a chat app.",
        context=tech_stack_context
    )
    print("\n--- Orchestrator Result 1 ---")
    print(result1)
    print("------------------------------------\n")

    print("\n--- Orchestrator Example 2: Backend API implementation (placeholder) ---")
    result2 = orchestrator.run( # Use the orchestrator instance from the factory
        prompt="Implement a REST API for posting and retrieving messages."
    )
    print("\n--- Orchestrator Result 2 ---")
    print(result2)
    print("------------------------------------\n")

    print("\n--- Orchestrator Example 3: Default handler (CodeWritingCrew) ---")
    result3 = orchestrator.run( # Use the orchestrator instance from the factory
        prompt="Write a python function that calculates factorial."
    )
    print("\n--- Orchestrator Result 3 ---")
    print(result3)
    print("------------------------------------\n")

if __name__ == "__main__":
    # Previous direct call to TechVettingCouncilCrew is already commented out.
    run_examples()
