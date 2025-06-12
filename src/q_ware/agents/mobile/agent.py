from crewai import Agent
# Assuming tools for the coordinator will be in ./tools.py
from .tools import my_tools
# Import sub-agent packages or specific agents if needed for direct reference,
# though delegation typically happens via tasks in a Crew.
# For now, we'll list them in the backstory for clarity.
# from .android import android_ui_agent, android_storage_agent, android_api_client_agent
# from .ios import ios_ui_agent, ios_storage_agent, ios_api_client_agent

mobile_project_coordinator_agent = Agent(
    role="Mobile Project Coordinator",
    goal="Oversee and coordinate all aspects of mobile application development for both Android and iOS platforms, "
         "ensuring timely delivery and adherence to project requirements and quality standards.",
    backstory=(
        "An experienced mobile project manager, this agent orchestrates the entire mobile development lifecycle. "
        "It translates high-level project goals into specific tasks for Android and iOS sub-agents, "
        "manages dependencies between tasks, and ensures seamless collaboration between the platform-specific teams. "
        "It is responsible for defining the mobile development strategy, selecting appropriate technologies "
        "(in consultation with other coordinators or architects if necessary), and ensuring that both "
        "Android and iOS applications meet the desired functionality and user experience. "
        "It delegates tasks to:\n\n"
        "- android_ui_agent\n"
        "- android_storage_agent\n"
        "- android_api_client_agent\n"
        "- ios_ui_agent\n"
        "- ios_storage_agent\n"
        "- ios_api_client_agent"
    ),
    tools=my_tools,
    allow_delegation=True, # This agent coordinates sub-agents
    verbose=True,
    llm="gemini/gemini-1.5-flash-latest"
)
