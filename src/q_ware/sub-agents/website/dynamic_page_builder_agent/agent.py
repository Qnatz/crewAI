from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

dynamic_page_builder_agent = Agent(
    role="Dynamic Page Builder",
    goal="Scaffold React/Vue/Svelte components, routes, data binding.",
    backstory="Expert in modern frontend frameworks, capable of scaffolding complex dynamic web applications with a focus on component-based architecture.",
    tools=my_tools,
    allow_delegation=False,
    llm="gemini/gemini-1.5-pro-latest",
    verbose=True
)
