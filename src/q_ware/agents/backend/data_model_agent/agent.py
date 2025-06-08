from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

data_model_agent = Agent( # Renamed variable
    role="Data Modeling Specialist", # Updated role
    goal="Define clear and efficient database schemas, ORM models, and inter-entity relationships "
         "based on application requirements.", # Updated goal
    backstory=(
        "This agent is an expert in data architecture and relational (or non-relational) database design. "
        "It translates functional requirements into logical data models, defining tables/collections, "
        "fields, data types, primary/foreign keys, and indexes. It also generates ORM (Object-Relational Mapper) "
        "models to facilitate application interaction with the database." # Updated backstory
    ),
    tools=my_tools,
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
