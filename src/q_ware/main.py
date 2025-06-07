# --- Sample Call for Tech Stack Committee ---
from q_ware.orchestrators.tech_stack_committee.crews.tech_stack_committee_crew import run_tech_stack_committee

if __name__ == "__main__":
    print("\n--- Running Tech Stack Committee ---")
    tech_stack_result = run_tech_stack_committee(
        project_idea="Build a real-time chat platform for remote teams with support for voice, video, and AI summarization",
        constraints="Budget under $20K, team familiar with TypeScript and Node.js, needs to scale to 10K users, must be GDPR compliant"
    )
    print("\n--- Tech Stack Committee Result ---")
    print(tech_stack_result)
    print("------------------------------------\n")
