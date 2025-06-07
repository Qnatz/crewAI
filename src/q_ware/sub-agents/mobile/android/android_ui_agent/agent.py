from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

android_ui_agent = Agent(
    role="Android UI Agent",
    goal="Build screens with Jetpack Compose / React Native views.",
    backstory="Specializes in creating user interfaces for Android applications using modern toolkits like Jetpack Compose or cross-platform solutions like React Native views.",
    tools=my_tools,
    allow_delegation=False,
    # llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
