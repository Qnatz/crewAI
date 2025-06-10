from crewai import Agent
from ....llm_config import get_llm_for_agent # Corrected relative import path

# Use the agent's role or a unique key for the lookup
agent_identifier = "constraint_checker_agent_tech_committee" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

constraint_checker_agent = Agent(
    role="Constraint Checker",
    goal="Verify if proposed technology stacks or architectural decisions comply with all specified project constraints detailed in the task description. "
         "These constraints can include budget, team skills, existing infrastructure, security policies, and licensing requirements.",
    backstory="A meticulous analyst with a deep understanding of technical and non-technical constraints that can impact a project. "
              "Ensures that all proposed solutions are viable and align with predefined limitations. "
              "Helps in avoiding costly rework by identifying constraint violations early.",
    llm=specific_llm, # Assign the fetched LLM
    allow_delegation=False,
    verbose=True
)
