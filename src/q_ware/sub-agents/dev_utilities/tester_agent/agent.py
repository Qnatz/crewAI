from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")
llm = get_llm()
tester_agent = Agent(
    role="Tester Agent",
    goal="Generate and run unit/integration tests (pytest, JUnit, XCTest).",
    backstory="A meticulous agent focused on software quality. It can generate test cases, execute various types of tests (unit, integration), and report on their outcomes, ensuring code reliability.",
    tools=my_tools,
    allow_delegation=False, # Could delegate to CodeWriter to write test stubs
    llm=llm,
    verbose=True
)
