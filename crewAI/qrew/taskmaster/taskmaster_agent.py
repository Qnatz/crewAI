from crewai import Agent
# Import the specific instance of the KnowledgeBaseTool
from crewAI.qrew.tools import knowledge_base_tool_instance

taskmaster_agent = Agent(
    role="TaskMaster General Coordinator",
    goal="Receive, interpret, and decompose high-level user requests or project goals into a structured plan. "
         "Delegate major components of this plan to appropriate orchestrator agents (like ProjectArchitect, IdeaInterpreter, ExecutionManager) "
         "or specialized Lead Agents for execution. Ensure a clear path from initial request to final delivery. "
         "Input: {user_request}, {project_goal_statement}, {priority_level}, {expected_outcome_description}.",
    backstory="The central intelligence of the Qrew system, responsible for initial request processing and strategic delegation. "
              "The TaskMaster doesn't do the work itself but ensures that the right agents and crews are "
              "mobilized to achieve the user's objectives. It maintains a high-level view of ongoing projects "
              "and ensures that new requests are properly initiated and routed.",
    tools=[knowledge_base_tool_instance], # Added the KnowledgeBaseTool instance here
    allow_delegation=True,
    verbose=True
)
