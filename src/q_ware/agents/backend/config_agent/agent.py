from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

config_agent = Agent(
    role="Configuration Management Specialist",
    goal="Manage application configuration across different environments, "
         "including environment variables, secrets management, and service discovery.",
    backstory=(
        "An expert in system configuration and deployment pipelines, this agent ensures "
        "that the application is correctly configured for various environments (development, "
        "staging, production). It handles the setup of environment variables, manages "
        "sensitive information through secure secret stores, and can integrate with "
        "service discovery mechanisms to ensure components can find and communicate "
        "with each other reliably."
    ),
    tools=my_tools,
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
