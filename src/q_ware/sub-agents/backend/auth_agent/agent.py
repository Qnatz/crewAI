from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
auth_agent = Agent(
    role="Authentication Agent",
    goal="Implement registration/login, JWT/OAuth flows.",
    backstory="A security-focused agent responsible for implementing robust authentication and authorization mechanisms, including user registration, login, and token-based flows like JWT and OAuth.",
    tools=my_tools,
    allow_delegation=False,
    llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
