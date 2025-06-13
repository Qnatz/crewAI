import json
from crewai import Crew, Process, Task
from ..lead_agents.backend_project_coordinator_agent.agent import backend_project_coordinator_agent
from ..lead_agents.web_project_coordinator_agent.agent import web_project_coordinator_agent
from ..lead_agents.mobile_project_coordinator_agent.agent import mobile_project_coordinator_agent
from ..lead_agents.devops_and_integration_coordinator_agent.agent import devops_and_integration_coordinator_agent

def run_crew_lead_workflow(inputs: dict):
    # Initialize crew leads for each domain
    backend_lead = backend_project_coordinator_agent
    web_lead = web_project_coordinator_agent
    mobile_lead = mobile_project_coordinator_agent
    devops_lead = devops_and_integration_coordinator_agent

    architecture_summary_str = json.dumps(inputs.get("architecture", {}), indent=2) # Added this line

    # Create tasks based on architecture
    tasks = [
        Task(
            description=f"Plan backend implementation for {inputs['project_name']}. "                         f"The overall project architecture summary is: {architecture_summary_str}",
            agent=backend_lead,
            expected_output="Backend implementation plan with task assignments"
        ),
        Task(
            description=f"Plan frontend implementation for {inputs['project_name']}. "                         f"The overall project architecture summary is: {architecture_summary_str}",
            agent=web_lead,
            expected_output="Frontend implementation plan with task assignments"
        ),
        Task(
            description=f"Plan mobile implementation for {inputs['project_name']}. "                         f"The overall project architecture summary is: {architecture_summary_str}",
            agent=mobile_lead,
            expected_output="Mobile implementation plan with task assignments"
        ),
        Task(
            description=f"Plan deployment for {inputs['project_name']}. "                         f"The overall project architecture summary is: {architecture_summary_str}",
            agent=devops_lead,
            expected_output="Deployment plan with task assignments"
        )
    ]

    # Execute crew lead planning
    crew = Crew(
        agents=[backend_lead, web_lead, mobile_lead, devops_lead],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    # Ensure result.tasks_output is not empty and has enough elements.
    # A more robust way would be to map tasks to their outputs if order isn't guaranteed
    # or if the number of tasks could vary. For now, assuming fixed order and count.
    backend_plan_output = result.tasks_output[0].raw if len(result.tasks_output) > 0 and hasattr(result.tasks_output[0], 'raw') else "Error: Backend task output not found or .raw attribute missing"
    frontend_plan_output = result.tasks_output[1].raw if len(result.tasks_output) > 1 and hasattr(result.tasks_output[1], 'raw') else "Error: Frontend task output not found or .raw attribute missing"
    mobile_plan_output = result.tasks_output[2].raw if len(result.tasks_output) > 2 and hasattr(result.tasks_output[2], 'raw') else "Error: Mobile task output not found or .raw attribute missing"
    deployment_plan_output = result.tasks_output[3].raw if len(result.tasks_output) > 3 and hasattr(result.tasks_output[3], 'raw') else "Error: Deployment task output not found or .raw attribute missing"

    return {
        "backend_plan": backend_plan_output,
        "frontend_plan": frontend_plan_output,
        "mobile_plan": mobile_plan_output,
        "deployment_plan": deployment_plan_output
    }
