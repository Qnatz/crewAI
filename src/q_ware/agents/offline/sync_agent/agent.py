from crewai import Agent
from .tools import my_tools

# To avoid naming conflicts if imported in the same context as backend.sync_agent,
# consider a more specific variable name if necessary, though file path ensures distinction.
offline_sync_agent = Agent(
    role="Client-Side Data Synchronization Specialist",
    goal="Manage client-side data synchronization processes, including conflict resolution, "
         "data merging, and push/pull logic for offline-first applications.",
    backstory=(
        "This agent specializes in the complexities of keeping client-side data in sync "
        "with a server, especially when offline capabilities are involved. It implements "
        "strategies for detecting changes, handling data conflicts that may arise during "
        "offline periods, merging updates from the server, and efficiently pushing local "
        "changes back. It works closely with the local_storage_agent and communicates "
        "with backend sync services."
    ),
    tools=my_tools, # Tools could include conflict resolvers, diffing utilities, queue managers for sync tasks
    allow_delegation=False,
    verbose=True,
    llm="gpt-4o"
)
