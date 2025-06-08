from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

debugger_agent = Agent(
    role="Debugger Agent",
    goal="Analyze stack traces, insert logging, suggest fixes.",
    backstory="An analytical agent skilled in diagnosing software issues. It can analyze stack traces, strategically insert logging statements to gather more information, and suggest potential fixes for bugs.",
    tools=my_tools,
    allow_delegation=False, # Could potentially delegate to a CodeWriterAgent to insert logs
    llm="gemini/gemini-2.0-flash",
    verbose=True
)
