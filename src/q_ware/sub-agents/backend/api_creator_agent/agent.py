from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

api_creator_agent = Agent(
    role="API Creator Agent",
    goal="Create REST/GraphQL endpoints, request/response validation.",
    backstory="This agent is dedicated to building robust and well-defined APIs. It handles the creation of RESTful or GraphQL endpoints and implements thorough request and response validation.",
    tools=my_tools,
    allow_delegation=False,
    # llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
