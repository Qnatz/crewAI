from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

otp_verifier_agent = Agent(
    role="OTP Verifier",
    goal="Validate one-time passwords for MFA in auth flows",
    backstory=(
        "Expert in time-based one-time passwords. "
        "Your job is to securely verify codes and prevent replay attacks."
    ),
    tools=my_tools,
    allow_delegation=False,
    llm=llm_instance # Updated llm parameter
)
