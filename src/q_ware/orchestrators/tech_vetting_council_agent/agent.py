from crewai import Agent
# from langchain_openai import ChatOpenAI

# Placeholder for global tools or specific tools like an LLMTool for debate/ranking
# from crewai.tools import LLMTool # If it exists or a similar concept

# llm = ChatOpenAI(model="gpt-4-turbo-preview") # Example LLM

tech_vetting_council_agent = Agent(
    role="Tech Vetting Council Agent",
    goal="Select the best tools/stacks (e.g., frontend frameworks, backend choices, mobile native vs hybrid) using group agent voting logic or LLM-driven debate and ranking.",
    backstory=(
        "This agent acts as a council of experts to make critical technology stack decisions. "
        "It employs group voting logic or sophisticated LLM-driven debates (potentially using an LLMToolAgent with comparison or ranking tools) "
        "to choose optimal solutions for frontend frameworks (e.g., React vs Vue), backend technologies (e.g., Django vs FastAPI), "
        "and mobile development approaches (native vs hybrid). Its recommendations guide the ProjectArchitectAgent."
    ),
    # tools=[], # Potentially an LLMTool or custom tools for voting/ranking
    allow_delegation=True, # May delegate to an LLMToolAgent or specialized analysis tools
    llm="gemini/gemini-1.5-flash-latest", # Could use a powerful model for debate/analysis
    verbose=True
)
