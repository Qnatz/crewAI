from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
data_model_agent = Agent(
    role="Data Model Agent",
    goal="Define ORM models or database schemas.",
    backstory="An agent specializing in data architecture, responsible for defining ORM (Object-Relational Mapping) models or database schemas to ensure data integrity and efficient data management.",
    tools=my_tools,
    allow_delegation=False,
    llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
