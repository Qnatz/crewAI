from crewai import Agent
from .tools import my_tools

otp_verifier_agent = Agent(
    role="OTP Verifier",
    goal="Validate one-time passwords for MFA in auth flows",
    backstory=(
        "Expert in time-based one-time passwords. "
        "Your job is to securely verify codes and prevent replay attacks."
    ),
    tools=my_tools,
    allow_delegation=False,
    llm="gpt-4o"
)
