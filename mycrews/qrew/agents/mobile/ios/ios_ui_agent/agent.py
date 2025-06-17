from crewai import Agent
from .....llm_config import get_llm_for_agent
from mycrews.qrew.tools.agenttools import get_tools_for_agent, AgentName

# Use the agent's role or a unique key for the lookup
agent_identifier = "ios_ui_agent" # Matching the key in MODEL_BY_AGENT
specific_llm = get_llm_for_agent(agent_identifier)

ios_ui_agent = Agent(
    role="iOS UI/UX Developer",
    goal="Design and implement user interfaces for iOS applications, focusing on usability and user experience",
    backstory="A creative iOS developer dedicated to crafting intuitive and visually appealing user interfaces that enhance user engagement.",
    llm=specific_llm, # Assign the fetched LLM
    tools=get_tools_for_agent(AgentName.MOBILE_UI_AGENT),
    allow_delegation=False,
    verbose=True,
    metadata={"type": "ios"}
)
