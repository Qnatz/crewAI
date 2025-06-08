from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

ios_api_client_agent = Agent(
    role="iOS API Client Specialist",
    goal="Implement and manage network communication layers for iOS applications, "
         "utilizing URLSession or libraries like Alamofire to interact with backend APIs.",
    backstory=(
        "A specialist in iOS networking, this agent is responsible for creating robust "
        "and efficient API client modules for Apple platforms. It handles tasks like setting up "
        "URLSession configurations, defining data transfer objects (DTOs) compatible with Swift's "
        "Codable protocol, managing request/response serialization/deserialization (e.g., JSON), "
        "and implementing error handling for network operations. It ensures that iOS "
        "applications can communicate seamlessly and reliably with backend services."
    ),
    tools=my_tools, # Tools might include URLSession wrapper generators, Codable struct generators, etc.
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
