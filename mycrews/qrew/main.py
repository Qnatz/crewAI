import sys
import os
# Add the project root (/app) to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Add the project's src directory to sys.path to allow 'from crewai import ...'
project_src_path = os.path.join(project_root, "src")
if project_src_path not in sys.path:
    sys.path.insert(1, project_src_path) # Insert after project_root

# Ensure the llm_config is loaded first to set up the default LLM
# This is crucial if agents are defined at the module level and instantiate their LLM upon import.
from .llm_config import default_llm # llm_config.py is now in the same directory

from .taskmaster import taskmaster_agent # Import the specific agent instance # type: ignore
# from mycrews.qrew.tools.knowledge_base_tool import knowledge_base_tool_instance # Removed after direct testing

# Enable LiteLLM debugging
os.environ["LITELLM_DEBUG"] = "1"

# taskmaster_agent now gets its LLM from its own definition file.
# The default_llm imported here is passed to the Crew instance.

from crewai import Task, Crew # type: ignore
from .main_workflow import run_idea_to_architecture_workflow # Added import

def run_qrew():
    print("Initializing Qrew System...")
    # Assuming llm_config.configured_llm is the one set by llm_config.py
    # Accessing it directly might not be standard if llm_config is just a script.
    # Better to rely on crewAI's global config if that's how it's meant to be used.
    # For now, we'll infer from environment variables for the error message.
    # print(f"Using LLM: {llm_config.llm_config.get()}") # This was the original line

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
        llm=default_llm, # Pass the configured LLM to the Crew
        verbose=True
    )

    print("\nKicking off TaskMasterAgent for initial request processing...")
    try:
        taskmaster_result = task_master_execution_crew.kickoff() # Renamed for clarity

        print("\nTaskMasterAgent Processing Complete.")
        print("--------------------------------------")
        print("Result/Project Brief from TaskMasterAgent:")
        if taskmaster_result:
            print(taskmaster_result.raw if hasattr(taskmaster_result, 'raw') else str(taskmaster_result))
        else:
            print("TaskMasterAgent produced no output.")
        print("--------------------------------------")

        # Check if TaskMasterAgent was successful and produced output
        if taskmaster_result and (taskmaster_result.raw if hasattr(taskmaster_result, 'raw') else str(taskmaster_result)):
            print("\nProceeding to Idea-to-Architecture Workflow...")

            # Define sample variables needed for the main_workflow inputs
            sample_stakeholder_feedback = "User retention is key. Gamification might be important. Mobile-first approach preferred."
            sample_market_research = "Competitors X and Y lack real-time interaction. Users want personalized training plans."
            sample_project_constraints = "Team has strong Python and React skills. Initial deployment on AWS. Budget for external services is moderate."
            sample_technical_vision = "A modular microservices architecture is preferred for scalability. Prioritize user data privacy."

            actual_workflow_inputs = {
                "user_idea": taskmaster_result.raw if hasattr(taskmaster_result, 'raw') else str(taskmaster_result),
                "stakeholder_feedback": sample_stakeholder_feedback,
                "market_research_data": sample_market_research,
                "constraints": sample_project_constraints,
                "technical_vision": sample_technical_vision
            }

            print(f"\nInputs for Idea-to-Architecture Workflow: {actual_workflow_inputs}")
            architecture_crew_result = run_idea_to_architecture_workflow(actual_workflow_inputs)

            print("\n\n####################################################")
            print("## Main Workflow (Idea-to-Architecture) Execution Result:")
            print("####################################################\n")
            if architecture_crew_result:
                print("Final output from the Architecture Crew:")
                print(architecture_crew_result.raw if hasattr(architecture_crew_result, 'raw') else str(architecture_crew_result))
            else:
                print("Architecture Crew produced no output or an error occurred.")
        else:
            print("\nTaskMasterAgent did not produce a valid output. Skipping Idea-to-Architecture Workflow.")

    except Exception as e:
        print(f"\nAn error occurred during Qrew execution: {e}")
        print("\nTroubleshooting Tips:")
        print("---------------------")

        error_str = str(e).lower()

        # Check LITELLM_MODEL to infer intended model type for better guidance
        litellm_model_env = os.environ.get("LITELLM_MODEL", "").lower()

        if "api_key" in error_str or "authentication" in error_str or "permission" in error_str:
            print("- The error suggests an API key issue or authentication failure.")
            if "openai" in error_str or "gpt" in litellm_model_env or "text-davinci" in litellm_model_env:
                print("  It seems you might be trying to use an OpenAI model.")
                print("  Please ensure your OPENAI_API_KEY environment variable is correctly set.")
            elif "gemini" in error_str or "gemini" in litellm_model_env:
                print("  It seems you might be trying to use a Gemini model.")
                print("  Please ensure your GEMINI_API_KEY environment variable is correctly set.")
            elif "anthropic" in error_str or "claude" in litellm_model_env:
                print("  It seems you might be trying to use an Anthropic (Claude) model.")
                print("  Please ensure your ANTHROPIC_API_KEY environment variable is correctly set.")
            # Add more specific model/provider checks here if needed
            else:
                print("  Please ensure the relevant API key (e.g., OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY) for your chosen LLM is set in your environment.")
            print("  Verify the key is valid and has the necessary permissions/credits.")

        elif "model_not_found" in error_str:
            print(f"- The error suggests the specified model ('{litellm_model_env}') could not be found.")
            print("  Please verify the LITELLM_MODEL environment variable is set to a valid model name for your chosen provider.")
            print("  If using a local LLM (e.g., Ollama), ensure the model is downloaded and available.")

        elif "context_length" in error_str or "context_window" in error_str:
            print("- The error suggests the input prompt is too long for the model's context window.")
            print("  Try reducing the length of your input or using a model with a larger context window.")

        else:
            print("- Please ensure your LLM is configured correctly.")
            print("  - If using a hosted LLM (OpenAI, Gemini, Anthropic, etc.), verify your API key and model name.")
            print("  - If using a local LLM (e.g., Ollama with LITELLM_MODEL=ollama/your_model or directly), ensure it's running and the model is accessible.")

        print("\nRefer to `crewAI/qrew/llm_config.py` to see how the LLM is being configured based on environment variables like LITELLM_MODEL, OPENAI_API_KEY, GEMINI_API_KEY, etc.")
        print("Ensure `litellm` is installed (`pip install litellm`).")

if __name__ == "__main__":
    run_qrew()
