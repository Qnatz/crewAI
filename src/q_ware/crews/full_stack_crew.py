from crewai import Crew, Task
from q_ware.agents.auth.auth_coordinator.agent import auth_coordinator_agent
# Import the new backend_coordinator_agent
from q_ware.agents.backend.agent import backend_coordinator_agent # Corrected import path
# Import the new mobile_project_coordinator_agent
from q_ware.agents.mobile.agent import mobile_project_coordinator_agent
# Import the new web_project_coordinator_agent
from q_ware.agents.web.agent import web_project_coordinator_agent
# Import the new offline_support_coordinator_agent
from q_ware.agents.offline.agent import offline_support_coordinator_agent
# Import the new devops_and_integration_coordinator_agent
from q_ware.agents.devops.agent import devops_and_integration_coordinator_agent
from q_ware.llm_config import get_llm

llm = get_llm()
full_stack_crew = Crew(
    name="FullStackCrew",
    llm=llm,
    agents=[
        auth_coordinator_agent,
        backend_coordinator_agent,
        mobile_project_coordinator_agent,
        web_project_coordinator_agent,
        offline_support_coordinator_agent,
        devops_and_integration_coordinator_agent, # Add the devops coordinator
    ],
    tasks=[
        Task(
          agent=auth_coordinator_agent,
          description="Set up authentication subsystem",
          expected_output="Successful completion of the task."
        ),
        Task(
            agent=backend_coordinator_agent,
            description="Orchestrate and develop all backend systems and APIs based on project requirements.",
            expected_output="Successful completion of the task."
        ),
        Task(
            agent=mobile_project_coordinator_agent,
            description="Coordinate the design and development of Android and iOS mobile applications.",
            expected_output="Successful completion of the task."
        ),
        Task(
            agent=web_project_coordinator_agent,
            description="Coordinate the design and development of the project website and web applications.",
            expected_output="Successful completion of the task."
        ),
        Task(
            agent=offline_support_coordinator_agent,
            description="Coordinate the implementation of offline-first capabilities, including local storage and data synchronization.",
            expected_output="Successful completion of the task."
        ),
        Task( # Add a task for the devops coordinator
            agent=devops_and_integration_coordinator_agent,
            description="Manage CI/CD pipelines, environment configurations, containerization, and overall integration testing.",
            expected_output="Successful completion of the task."
        ),
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
