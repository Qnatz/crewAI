from crewai import Agent
from .tools import my_tools # Tools specific to the offline coordinator
# Import sub-agents for clarity in backstory or potential direct reference.
# from .local_storage_agent import local_storage_agent
# from .sync_agent import offline_sync_agent # Client-side sync agent

offline_support_coordinator_agent = Agent(
    role="Offline Support Coordinator",
    goal="Oversee and coordinate the implementation of all offline capabilities, "
         "including local data storage and data synchronization strategies for applications "
         "designed to be offline-first or operate reliably with intermittent connectivity.",
    backstory=(
        "An expert in offline-first application architecture, this agent orchestrates "
        "the efforts of sub-agents responsible for on-device storage and client-side "
        "data synchronization. It ensures that applications provide a seamless user "
        "experience even when network connectivity is unavailable or unreliable. "
        "It defines the overall offline strategy, manages how data is stored locally, "
        "and coordinates how and when data is synced with the backend. It delegates tasks to:\n\n"
        "- local_storage_agent\n"
        "- offline_sync_agent (client-side sync)"
    ),
    tools=my_tools,
    allow_delegation=True, # This agent coordinates sub-agents
    verbose=True,
    llm="gpt-4o"
)
