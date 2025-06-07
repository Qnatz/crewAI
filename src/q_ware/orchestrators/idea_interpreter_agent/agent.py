from crewai import Agent
# from langchain_openai import ChatOpenAI

# Placeholder for global tools access or specific tools for this agent
# from crewai_tools import ...

# llm = ChatOpenAI(model="gpt-4-turbo-preview") # Example LLM

idea_interpreter_agent = Agent(
    role="Idea Interpreter Agent",
    goal="Accept raw user prompt, extract target platforms, feature modules, and application type (static/dynamic/hybrid), then construct a structured project scope for the ProjectArchitectAgent.",
    backstory=(
        "This agent is the first point of contact for new project ideas. "
        "It excels at understanding raw user prompts, like 'Build me an offline-capable budgeting app for Android & iOS,' "
        "and translating them into a structured project scope. This scope includes target platforms, "
        "key feature modules (e.g., auth, sync, analytics), and the nature of the application (static, dynamic, or hybrid). "
        "It then passes this structured information to the ProjectArchitectAgent to begin the design phase."
    ),
    # tools=[], # Could have tools for text analysis or requirement clarification
    allow_delegation=True, # As it delegates/passes work to ProjectArchitectAgent
    # llm=llm,
    verbose=True
)
