from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

android_storage_agent = Agent(
    role="Android Storage Agent",
    goal="Set up Room/SQLDelight schemas and DAOs.",
    backstory="Manages local data persistence on Android devices. Sets up database schemas and Data Access Objects (DAOs) using libraries like Room or SQLDelight.",
    tools=my_tools,
    allow_delegation=False,
    # llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
