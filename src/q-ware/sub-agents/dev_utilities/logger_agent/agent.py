from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

logger_agent = Agent(
    role="Logger Agent",
    goal="Collect and format agent logs, produce audit trails.",
    backstory="An agent dedicated to meticulous record-keeping. It collects logs from various agents, formats them consistently, and produces comprehensive audit trails for monitoring and debugging purposes.",
    tools=my_tools,
    allow_delegation=False,
    # llm=llm,
    verbose=True
)
