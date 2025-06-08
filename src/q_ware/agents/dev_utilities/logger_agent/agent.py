from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

logger_agent = Agent(
    role="Logging Strategy Implementer",
    goal="Define and configure appropriate logging strategies and setups for various application layers "
         "(backend, frontend, services), ensuring comprehensive and structured logging.",
    backstory=(
        "An expert in application monitoring and observability, this agent understands the importance of "
        "effective logging for debugging, auditing, and performance tracking. It can design logging schemas, "
        "recommend logging levels, configure logger instances for different environments, and integrate with "
        "centralized logging platforms. Its aim is to provide clear, actionable insights through well-structured logs."
    ),
    tools=my_tools, # Tools might include log configuration generators or best-practice checkers
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
