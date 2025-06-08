from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

sync_agent = Agent(
    role="Backend Data Synchronization Specialist",
    goal="Implement backend logic required for robust data synchronization, "
         "supporting offline-first application capabilities and delta state management.",
    backstory=(
        "This agent focuses on the backend mechanisms that enable seamless data flow "
        "between client applications and the server, especially for scenarios requiring "
        "offline functionality. It designs and implements APIs and logic for handling "
        "data conflicts, merging delta states, and ensuring eventual consistency "
        "for applications that need to operate with intermittent connectivity."
    ),
    tools=my_tools,
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
