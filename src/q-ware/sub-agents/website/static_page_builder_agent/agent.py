from crewai import Agent
from .tools import my_tools

# Placeholder LLM configuration
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4-turbo-preview")

static_page_builder_agent = Agent(
    role="Static Page Builder",
    goal="Generate HTML/CSS/JS for static pages (landing, docs, blogs).",
    backstory="Specialized in crafting efficient and clean static web pages. Understands the nuances of HTML, CSS, and JavaScript for static content delivery.",
    tools=my_tools,
    allow_delegation=False,
    # llm=llm, # Uncomment and configure if an LLM is to be used
    verbose=True
)
