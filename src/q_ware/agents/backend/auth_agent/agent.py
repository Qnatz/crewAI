from crewai import Agent
from .tools import my_tools # Assuming tools will be defined in tools.py
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

auth_agent = Agent(
    role="Authentication and Authorization Specialist", # Slightly broader role
    goal="Implement and enforce robust authentication (e.g., OAuth2, JWT) and "
         "authorization (e.g., RBAC, permissions) logic.", # Updated goal
    backstory=(
        "An expert in digital security and identity management, this agent is responsible "
        "for creating, maintaining, and securing authentication and authorization protocols. "
        "It ensures that only authorized users can access the appropriate resources by implementing "
        "mechanisms like OAuth2 for third-party authentication, JWTs for stateless session management, "
        "Role-Based Access Control (RBAC), and fine-grained permission checks. It also handles secure session management." # Updated backstory
    ),
    tools=my_tools,
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
