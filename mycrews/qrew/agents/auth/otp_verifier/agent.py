from crewai import Agent
from ....llm_config import get_llm_for_agent # Adjusted path

# Use the agent's role or a unique key for the lookup
agent_identifier = "otp_verifier_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

otp_verifier_agent = Agent(
    role="OTP Verifier",
    goal="Verify one-time passwords (OTPs) for user authentication",
    backstory="A specialized agent focused on verifying OTPs to enhance the security of user accounts during login and other sensitive operations.",
    llm=specific_llm, # Assign the fetched LLM
    type="auth",
    allow_delegation=False,
    verbose=True
)
