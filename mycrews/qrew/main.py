import sys
import os
import logging
# Add the project root (/app) to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Add the project's src directory to sys.path
project_src_path = os.path.join(project_root, "src")
if project_src_path not in sys.path:
    sys.path.insert(1, project_src_path)

# Configure LiteLLM logging BEFORE importing any crewAI modules
os.environ["LITELLM_LOG"] = "DEBUG"  # More detailed logging
logging.basicConfig(level=logging.DEBUG)

# Import LLM configuration
from .llm_config import default_llm

# Import agents after configuring logging
from .taskmaster import taskmaster_agent
from .main_workflow import run_idea_to_architecture_workflow

from crewai import Task, Crew
from litellm import completion  # For direct API test

def test_llm_connection():
    """Test LLM connection before crew execution"""
    print("\n🧪 Testing LLM connection...")
    try:
        test_prompt = [{"content": "Hello world", "role": "user"}]
        response = completion(
            model=os.getenv("LITELLM_MODEL", "gpt-3.5-turbo"),
            messages=test_prompt,
            max_tokens=10
        )
        print("✅ LLM Connection Successful!")
        print(f"Test Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ LLM Connection Failed: {str(e)}")
        print("\nTroubleshooting Steps:")
        print("1. Verify API key in environment variables")
        print("2. Check model name in LITELLM_MODEL")
        print("3. Test network connectivity to API endpoint")
        return False

def run_qrew():
    print("Initializing Qrew System...")

    # Step 1: Test LLM connection before proceeding
    if not test_llm_connection():
        print("Aborting workflow due to LLM configuration issues")
        return

    # Sample data
    sample_user_request = "I need a new mobile app for tracking personal fitness goals. It should be fun and engaging."
    sample_project_goal = "Develop a market-leading mobile fitness tracking application."
    sample_priority = "High"

    print(f"\nReceived User Request: '{sample_user_request}'")
    print(f"Project Goal: '{sample_project_goal}'")
    print(f"Priority: {sample_priority}")

    # Create task with simplified description
    taskmaster_initial_task = Task(
        description=f"Analyze user request: '{sample_user_request}'. Project goal: '{sample_project_goal}'.",
        expected_output="Clear project brief with scope, objectives, and next steps",
        agent=taskmaster_agent,
        inputs={'user_request': sample_user_request}
    )

    # Create crew with unified LLM configuration
    task_master_execution_crew = Crew(
        agents=[taskmaster_agent],
        tasks=[taskmaster_initial_task],
        llm=default_llm,  # Unified LLM config
        verbose=2  # Maximum verbosity
    )

    print("\nKicking off TaskMasterAgent...")
    try:
        taskmaster_result = task_master_execution_crew.kickoff()

        # Process results
        print("\nTaskMasterAgent Processing Complete.")
        if taskmaster_result:
            print(f"Result: {taskmaster_result}")

            # Prepare workflow inputs
            workflow_inputs = {
                "user_idea": str(taskmaster_result),
                "stakeholder_feedback": "User retention is key. Mobile-first approach.",
                "market_research_data": "Competitors lack real-time interaction",
                "constraints": "Team: Python/React. AWS deployment.",
                "technical_vision": "Microservices for scalability"
            }

            # Execute next workflow
            print("\nStarting Idea-to-Architecture Workflow...")
            architecture_result = run_idea_to_architecture_workflow(workflow_inputs)
            print(f"\nArchitecture Result: {architecture_result}")

        else:
            print("TaskMasterAgent produced no output.")

    except Exception as e:
        print(f"\n🚨 Critical Workflow Failure: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_qrew()
