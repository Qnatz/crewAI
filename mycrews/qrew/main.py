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
    sys.path.insert(1, project_src_path) # Insert after project_root

# Ensure the llm_config is loaded first to set up the default LLM
# This is crucial if agents are defined at the module level and instantiate their LLM upon import.
from .llm_config import default_llm # llm_config.py is now in the same directory
from . import config as crew_config # This will execute config.py and set Task.DEFAULT_SCHEMA

from .taskmaster import taskmaster_agent # Import the specific agent instance # type: ignore
# from mycrews.qrew.tools.knowledge_base_tool import knowledge_base_tool_instance # Removed after direct testing

# Enable LiteLLM debugging
os.environ["LITELLM_DEBUG"] = "1"

# taskmaster_agent now gets its LLM from its own definition file.
# The default_llm imported here is passed to the Crew instance.

from crewai import Task, Crew, Process # type: ignore
from .workflows.orchestrator import WorkflowOrchestrator

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
        # input parameter removed as values are in f-string description
        successCriteria=[
            "project brief created",
            "scope defined",
            "objectives defined",
            "key deliverables listed",
            "complexity assessed",
            "recommendation for next step provided"
        ]
    )

    # To execute this task, we use the qrew_main_crew
    # taskmaster_agent is now pre-registered in qrew_main_crew in main_workflow.py

    try:
        # Create a temporary crew for taskmaster execution
        taskmaster_crew = Crew(
            agents=[taskmaster_agent],
            tasks=[],  # Task is executed directly
            process=Process.sequential,
            verbose=True
        )

        print("\nExecuting TaskMasterAgent for initial request processing...")
        # Assign the task to the crew and kickoff
        taskmaster_crew.tasks = [taskmaster_initial_task]
        task_execution_result = taskmaster_crew.kickoff()

        # Process the result from kickoff()
        taskmaster_result_str = "" # Initialize to empty string

        # kickoff() usually returns a final TaskOutput for a simple sequential crew with one task,
        # or a list of TaskOutputs if there were multiple tasks or complex interactions.
        # For a single task, it's often the direct TaskOutput.
        final_task_output = None
        if isinstance(task_execution_result, list) and len(task_execution_result) > 0:
            # If kickoff returns a list, assume the last output is the most relevant for a sequential flow.
            # Or, if it's known to be the first/only, access it directly.
            # For a crew with a single task, the first item (if a list) is the one.
            final_task_output = task_execution_result[0]
        elif hasattr(task_execution_result, 'raw_output'): # Check if it's a TaskOutput-like object
            final_task_output = task_execution_result
        elif task_execution_result is not None: # If it's some other non-None result
             taskmaster_result_str = str(task_execution_result)

        # Extract string from the final_task_output if it was found
        if final_task_output:
            if hasattr(final_task_output, 'raw_output') and final_task_output.raw_output:
                taskmaster_result_str = final_task_output.raw_output
            elif hasattr(final_task_output, 'raw') and final_task_output.raw: # Fallback
                taskmaster_result_str = final_task_output.raw
            elif isinstance(final_task_output, str):
                taskmaster_result_str = final_task_output
            else:
                taskmaster_result_str = str(final_task_output)

        # Ensure the variable used by subsequent code is assigned
        taskmaster_result = taskmaster_result_str

        print("\nTaskMasterAgent Processing Complete.")
        print("--------------------------------------")
        print("Result/Project Brief from TaskMasterAgent:")
        print(taskmaster_result) # Print the extracted string
        print("--------------------------------------")

        # Check if TaskMasterAgent was successful and produced output
        if taskmaster_result and taskmaster_result.strip():
            print("\nProceeding to development pipeline...")

            # Define sample variables needed for the main_workflow inputs
            sample_stakeholder_feedback = "User retention is key. Gamification might be important. Mobile-first approach preferred."
            sample_market_research = "Competitors X and Y lack real-time interaction. Users want personalized training plans."
            sample_project_constraints = "Team has strong Python and React skills. Initial deployment on AWS. Budget for external services is moderate."
            sample_technical_vision = "A modular microservices architecture is preferred for scalability. Prioritize user data privacy."

            pipeline_inputs = {
                "user_idea": taskmaster_result, # This comes from the TaskMasterAgent
                "project_name": "FitnessTrackerApp", # Example from issue
                "stakeholder_feedback": sample_stakeholder_feedback,
                "market_research_data": sample_market_research,
                "constraints": sample_project_constraints,
                "technical_vision": sample_technical_vision
            }

            orchestrator = WorkflowOrchestrator()
            results = orchestrator.execute_pipeline(pipeline_inputs)

            print("\nPipeline Execution Complete")
            print("===========================")
            print("Final Output:", results["final_output"])

            # Save artifacts
            with open("architecture.json", "w") as f:
                json.dump(results["architecture"], f, indent=2)

            with open("crew_assignments.json", "w") as f:
                json.dump(results["crew_assignments"], f, indent=2)

            print("\nArchitecture Design:")
            print(json.dumps(results["architecture"], indent=2))
            print("\nCrew Assignments:")
            print(json.dumps(results["crew_assignments"], indent=2))
            print("\nDeveloped Components:")
            if isinstance(results["components"], (dict, list)):
                 print(json.dumps(results["components"], indent=2))
            else:
                print(results["components"])

        else:
            print("\nTaskMasterAgent did not produce a valid output. Skipping development pipeline.")

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
