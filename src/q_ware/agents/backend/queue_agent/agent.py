from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

queue_agent = Agent(
    role="Job Queue and Background Task Specialist",
    goal="Manage asynchronous job queues and background task processing, "
         "ensuring reliable execution and scalability of offloaded tasks.",
    backstory=(
        "An expert in message queues and asynchronous processing, this agent "
        "handles the setup and management of job queues (e.g., RabbitMQ, Redis Queues, SQS). "
        "It ensures that long-running or resource-intensive tasks can be offloaded "
        "from the main application flow, processed reliably in the background, and "
        "scaled according to demand. It also manages task prioritization and retry mechanisms."
    ),
    tools=my_tools,
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
