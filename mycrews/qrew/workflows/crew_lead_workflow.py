from crewai import Crew, Process, Task
from ..agents.crew_lead_agent import CrewLeadAgent

def run_crew_lead_workflow(inputs: dict):
    # Initialize crew leads for each domain
    backend_lead = CrewLeadAgent("BackendDevelopmentCrew")
    web_lead = CrewLeadAgent("WebDevelopmentCrew")
    mobile_lead = CrewLeadAgent("MobileDevelopmentCrew")
    devops_lead = CrewLeadAgent("DevOpsCrew")

    # Create tasks based on architecture
    tasks = [
        Task(
            description=f"Plan backend implementation for {inputs['project_name']}",
            agent=backend_lead,
            expected_output="Backend implementation plan with task assignments",
            context=inputs["architecture"]
        ),
        Task(
            description=f"Plan frontend implementation for {inputs['project_name']}",
            agent=web_lead,
            expected_output="Frontend implementation plan with task assignments",
            context=inputs["architecture"]
        ),
        Task(
            description=f"Plan mobile implementation for {inputs['project_name']}",
            agent=mobile_lead,
            expected_output="Mobile implementation plan with task assignments",
            context=inputs["architecture"]
        ),
        Task(
            description=f"Plan deployment for {inputs['project_name']}",
            agent=devops_lead,
            expected_output="Deployment plan with task assignments",
            context=inputs["architecture"]
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
    return {
        "backend_plan": result[0],
        "frontend_plan": result[1],
        "mobile_plan": result[2],
        "deployment_plan": result[3]
    }
