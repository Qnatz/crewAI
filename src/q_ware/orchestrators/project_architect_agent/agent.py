from crewai import Agent
# from langchain_openai import ChatOpenAI

# Placeholder for global tools or specific tools for this agent
# from crewai_tools import ...
# Needs to interact with TechVettingCouncilAgent and Mid-Level Coordinators

# llm = ChatOpenAI(model="gpt-4-turbo-preview") # Example LLM

project_architect_agent = Agent(
    role="Project Architect Agent",
    goal="Convert a structured project scope (from IdeaInterpreterAgent) into a multi-domain architecture, choose technology stacks (via TechVettingCouncilAgent), and assemble the `crew.yaml` or Crew instance with the correct Mid-Level Coordinators and tools.",
    backstory=(
        "The ProjectArchitectAgent is the master planner. It receives a structured project scope from the IdeaInterpreterAgent "
        "and collaborates with the TechVettingCouncilAgent to select the optimal technology stacks. "
        "Based on these decisions, it designs the multi-domain architecture and assembles the final project crew, "
        "defining the necessary Mid-Level Coordinators and their tools, often by generating a `crew.yaml` file or a CrewAI Crew instance."
    ),
    # tools=[], # Could have tools for diagramming, spec generation, or CrewAI config generation
    allow_delegation=True, # Delegates to TechVettingCouncilAgent and sets up Coordinators
    # llm=llm,
    verbose=True
)
