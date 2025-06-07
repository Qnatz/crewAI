from crewai import Agent
from crewai import Task
# Ensure the import path is correct based on the new directory structure
from q_ware.agents.auth.otp_verifier.agent import otp_verifier_agent
from q_ware.agents.auth.otp_verifier.tools import verify_otp

auth_coordinator_agent = Agent(
    role="Auth Coordinator",
    goal="Implement end-to-end authentication flow (register, login, MFA)",
    backstory=(
        "You orchestrate user registration, login, token issuance, "
        "and OTP validation by delegating to sub-agents."
    ),
    tools=[verify_otp], # Assuming verify_otp is a tool it can use directly or delegate
    allow_delegation=True,
    llm="gpt-4o"
)

# Define its internal workflow
# According to the crewAI documentation, add_subtasks is not a method of the Agent class.
# Tasks are typically defined within a Crew context, not directly added to an agent this way.
# For now, I will comment out the add_subtasks part as it might be conceptual
# or require a different implementation approach with the current crewAI version.
# If there's a specific way `add_subtasks` is implemented in your environment,
# this might need adjustment.

# auth_coordinator_agent.add_subtasks([
#     Task(
#       agent=None, # Or a specific agent if available
#       description="1. Create user registration endpoint"
#     ),
#     Task(
#       agent=None, # Or a specific agent if available
#       description="2. Create login endpoint with JWT issuance"
#     ),
#     Task(
#       agent=otp_verifier_agent,
#       description="3. Delegate to OTP Verifier for MFA"
#     ),
# ])
