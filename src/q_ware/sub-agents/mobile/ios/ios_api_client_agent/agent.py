from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
ios_api_client_agent = Agent(
    role="iOS API Client Agent",
    goal="Configure URLSession/Alamofire clients, handle auth tokens.",
    backstory="Manages network communication for iOS apps. Configures HTTP clients using URLSession or Alamofire and handles authentication tokens for secure API interactions.",
    tools=my_tools,
    allow_delegation=False,
    llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
