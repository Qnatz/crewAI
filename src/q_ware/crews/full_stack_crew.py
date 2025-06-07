from crewai import Crew, Task
# Ensure the import path is correct based on the new directory structure
from q_ware.agents.auth.auth_coordinator.agent import auth_coordinator_agent
# (you’d import other coordinators here similarly)
# from q_ware.agents.backend.backend_coordinator.agent import backend_coordinator_agent
# from q_ware.agents.web.web_coordinator.agent import web_coordinator_agent

full_stack_crew = Crew(
    name="FullStackCrew",
    agents=[
        auth_coordinator_agent,
        # backend_coordinator_agent,
        # web_coordinator_agent,
        # mobile_coordinator_agent,
    ],
    tasks=[
        Task(
          agent=auth_coordinator_agent,
          description="Set up authentication subsystem"
        ),
        # Task(agent=backend_coordinator_agent, description="…"),
        # Task(agent=web_coordinator_agent, description="…"),
    ]
)

# The issue mentions:
# # Kick off full project
# full_stack_crew.tasks.insert(0, Task(
#     agent=None,
#     description="Start full-stack development: auth → backend → web → mobile"
# ))
# full_stack_crew.run()
# This looks like example usage code, not part of the crew definition itself.
# So, it will not be included in this file directly unless specified otherwise.
