from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

android_api_client_agent = Agent(
    role="Android API Client Agent",
    goal="Configure Retrofit/Ktor clients, handle auth tokens.",
    backstory="Expert in setting up and managing network communication for Android apps. Configures HTTP clients like Retrofit or Ktor and handles authentication tokens securely.",
    tools=my_tools,
    allow_delegation=False,
    # llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
