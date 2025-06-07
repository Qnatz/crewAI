from crewai import Agent
from .tools import my_tools

android_api_client_agent = Agent(
    role="Android API Client Specialist",
    goal="Implement and manage network communication layers for Android applications, "
         "typically using libraries like Retrofit to interact with backend APIs.",
    backstory=(
        "A specialist in Android networking, this agent is responsible for creating robust "
        "and efficient API client modules. It handles tasks like setting up Retrofit interfaces, "
        "defining data transfer objects (DTOs), managing request/response serialization/deserialization, "
        "and implementing error handling for network operations. It ensures that the Android "
        "application can communicate seamlessly and reliably with backend services."
    ),
    tools=my_tools, # Tools might include Retrofit interface generators, DTO converters, etc.
    allow_delegation=False,
    verbose=True,
    llm="gpt-4o"
)
