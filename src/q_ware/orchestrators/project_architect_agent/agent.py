from crewai import Agent
from .tools import my_tools

project_architect_agent = Agent(
    role="System Architect and Design Lead",
    goal="Design a robust, scalable, and maintainable high-level system architecture "
         "based on the project blueprint provided by the idea_interpreter_agent. This includes "
         "defining major components, modules, data flows, API contracts, and technology stack considerations.",
    backstory=(
        "A seasoned solutions architect with broad knowledge across various technology domains. "
        "This agent takes the structured blueprint from the idea_interpreter_agent and translates it "
        "into a comprehensive architectural design. It considers aspects like scalability, performance, "
        "security, maintainability, and cost. It produces architectural diagrams, defines module "
        "responsibilities, specifies key technology choices (e.g., database types, messaging systems, "
        "frameworks), and outlines the overall data and service interaction model. Its output is crucial "
        "for the tech_vetting_council_agent and the execution_manager_agent."
    ),
    tools=my_tools, # Tools could include diagramming tools, modeling software, tech stack databases
    allow_delegation=True, # Could delegate specific research or modeling tasks if sub-architects existed
    verbose=True,
    llm="gpt-4o"
)
