# --- Main Q-Ware Entrypoint ---
from q_ware.taskmaster.taskmaster_agent import TaskmasterAgent

def run_examples():
    taskmaster = TaskmasterAgent()

    print("\n--- Taskmaster Example 1: Tech stack recommendation ---")
    # For tech_vetting, context for constraints might be useful
    tech_stack_context = {
        "constraints": "Budget under $20K, team familiar with TypeScript and Node.js, needs to scale to 10K users, must be GDPR compliant"
    }
    result1 = taskmaster.run(
        prompt="I need a fast and scalable tech stack for a chat app.",
        context=tech_stack_context
    )
    print("\n--- Taskmaster Result 1 ---")
    print(result1)
    print("------------------------------------\n")

    print("\n--- Taskmaster Example 2: Backend API implementation (placeholder) ---")
    # This will currently go to the placeholder ExecutionManagerCrew
    result2 = taskmaster.run(
        prompt="Implement a REST API for posting and retrieving messages."
    )
    print("\n--- Taskmaster Result 2 ---")
    print(result2)
    print("------------------------------------\n")

    print("\n--- Taskmaster Example 3: Default handler (CodeWritingCrew) ---")
    result3 = taskmaster.run(
        prompt="Write a python function that calculates factorial."
    )
    print("\n--- Taskmaster Result 3 ---")
    print(result3)
    print("------------------------------------\n")


if __name__ == "__main__":
    # Remove or comment out the previous tech_stack_committee direct call if it exists
    # from q_ware.orchestrators.tech_stack_committee.crews.tech_vetting_council_crew import TechVettingCouncilCrew
    # print("\n--- Running Tech Stack Committee Directly (Old Example - for reference) ---")
    # tech_stack_crew = TechVettingCouncilCrew(
    # project_idea="Build a real-time chat platform for remote teams with support for voice, video, and AI summarization",
    # constraints="Budget under $20K, team familiar with TypeScript and Node.js, needs to scale to 10K users, must be GDPR compliant"
    # )
    # tech_stack_result = tech_stack_crew.run()
    # print("\n--- Tech Stack Committee Result (Old Example) ---")
    # print(tech_stack_result)
    # print("------------------------------------\n")

    run_examples()
