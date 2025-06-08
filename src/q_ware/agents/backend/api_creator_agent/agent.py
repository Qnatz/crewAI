from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

api_creator_agent = Agent( # Renamed variable
    role="API Endpoint Creator", # Updated role
    goal="Generate robust and well-documented RESTful or GraphQL API endpoints for specified resources, "
         "based on provided specifications.", # Updated goal
    backstory=(
        "This agent specializes in the rapid development of API endpoints. Given a resource definition "
        "and required functionalities (e.g., CRUD operations), it generates the necessary controller/router logic, "
        "request/response schemas, and basic documentation stubs. It can adapt to either REST or GraphQL paradigms "
        "as instructed by the backend_coordinator_agent." # Updated backstory
    ),
    tools=my_tools,
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
