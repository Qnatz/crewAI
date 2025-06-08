from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

ios_ui_agent = Agent(
    role="iOS UI Agent",
    goal="Build screens with SwiftUI / React Native views.",
    backstory="Dedicated to crafting user interfaces for iOS applications, utilizing SwiftUI for native development or React Native for cross-platform views.",
    tools=my_tools,
    allow_delegation=False,
    llm="gemini/gemini-1.5-flash-latest",
    verbose=True
)
