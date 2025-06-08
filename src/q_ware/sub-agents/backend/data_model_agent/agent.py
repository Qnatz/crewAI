from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

data_model_agent = Agent(
    role="Data Model Agent",
    goal="Define ORM models or database schemas.",
    backstory="An agent specializing in data architecture, responsible for defining ORM (Object-Relational Mapping) models or database schemas to ensure data integrity and efficient data management.",
    tools=my_tools,
    allow_delegation=False,
    llm="gemini/gemini-1.5-flash-latest",
    verbose=True
)
