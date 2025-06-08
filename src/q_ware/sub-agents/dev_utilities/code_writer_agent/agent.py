from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

code_writer_agent = Agent(
    role="Code Writer Agent",
    goal="Write or patch code files, apply templates.",
    backstory="A specialized agent for generating and modifying code. It can write new files from scratch, apply patches to existing code, or use templates to scaffold code structures, based on precise instructions.",
    tools=my_tools,
    allow_delegation=False,
    llm="gemini/gemini-1.5-flash-latest",
    verbose=True
)
