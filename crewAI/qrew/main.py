# Ensure the llm_config is loaded first to set up the default LLM
# This is crucial if agents are defined at the module level and instantiate their LLM upon import.
try:
    from . import llm_config # This will execute llm_config.py
except ImportError:
    # Handle cases where main.py might be run as a top-level script for testing
    # and relative imports don't work as expected.
    import llm_config

from crewAI.qrew.taskmaster import taskmaster_agent # Import the specific agent instance
# from crewAI.qrew.taskmaster.crews import TaskMasterCrew # If TaskMaster had its own crew for kickoff

# For this initial version, we'll directly use the TaskMasterAgent and its tasks.
# We need a way to get the tasks associated with the TaskMasterAgent.
# If tasks are defined in YAML, the agent or a helper would load them.
# If tasks are defined in a crew, we'd instantiate the crew.

# Let's assume the TaskMasterAgent's tasks are defined in its tasks.yaml
# and we need a way to load and run one of them.
# For simplicity in this step, we'll manually define the input for the first task
# of TaskMasterAgent which is "Analyze and Delegate User Request".

# The TaskMasterAgent's first task (from its tasks.yaml) is:
# - description: >
#     Analyze the incoming {user_request} or {project_goal_statement}.
#     Clarify ambiguities and define the primary objectives, scope, and desired outcomes.
#     Consult with the IdeaInterpreterAgent if the request is vague or needs significant refinement.
#     Input: {user_request}, {project_goal_statement}, {priority_level}.
#   expected_output: >
#     A clear and concise project brief...
#   agent: taskmaster_agent

from crewai import Task

def run_qrew():
    print("Initializing Qrew System...")
    print(f"Using LLM: {llm_config.llm_config.get()}") # Verify which LLM was configured

    # Sample user request
    sample_user_request = "I need a new mobile app for tracking personal fitness goals. It should be fun and engaging."
    sample_project_goal = "Develop a market-leading mobile fitness tracking application."
    sample_priority = "High"

    print(f"\nReceived User Request: '{sample_user_request}'")
    print(f"Project Goal: '{sample_project_goal}'")
    print(f"Priority: {sample_priority}")

    # Define the task for the TaskMasterAgent based on its first defined task
    # This simulates how an orchestrator might prepare and assign a task.
    taskmaster_initial_task = Task(
        description=f"Analyze the incoming user request: '{sample_user_request}' "
                    f"and project goal statement: '{sample_project_goal}'. "
                    "Clarify ambiguities, define primary objectives, scope, and desired outcomes. "
                    "Consult with the IdeaInterpreterAgent if the request is vague or needs significant refinement. "
                    "Determine the next steps for delegation.",
        expected_output="A clear and concise project brief, including defined scope and objectives, "
                        "key deliverables, success criteria, initial assessment of complexity, "
                        "and a recommendation for the next orchestrator or Lead Agent.",
        agent=taskmaster_agent, # Assign the imported agent instance
        inputs={ # Provide the inputs expected by the task description placeholders
            'user_request': sample_user_request,
            'project_goal_statement': sample_project_goal,
            'priority_level': sample_priority
        }
    )

    # To execute this task, we'd typically add it to a Crew and kick it off.
    # Since TaskMasterAgent is a high-level coordinator, it might be part of a simple
    # "TaskMasterCrew" or we can create a temporary crew here for execution.
    from crewai import Crew

    # Create a temporary crew for the TaskMasterAgent to execute its initial task
    # In a more complex setup, TaskMaster might have its own defined crew in taskmaster/crews/
    task_master_execution_crew = Crew(
        agents=[taskmaster_agent],
        tasks=[taskmaster_initial_task],
        verbose=True
    )

    print("\nKicking off TaskMasterAgent for initial request processing...")
    try:
        result = task_master_execution_crew.kickoff()

        print("\nTaskMasterAgent Processing Complete.")
        print("--------------------------------------")
        print("Result/Project Brief:")
        print(result)
        print("--------------------------------------")

    except Exception as e:
        print(f"An error occurred during TaskMasterAgent execution: {e}")
        print("Please ensure your LLM is configured correctly (e.g., API keys are set).")
        print("If using a local LLM like Ollama, ensure it is running and the model is available.")

if __name__ == "__main__":
    run_qrew()
