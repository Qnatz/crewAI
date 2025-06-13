from crewai import Crew, Process, Task
from ..agents.backend import api_creator_agent, data_model_agent
from ..agents.web import dynamic_page_builder_agent
from ..agents.mobile import android_ui_agent, ios_ui_agent
from ..agents.devops import devops_agent

def run_subagent_execution_workflow(inputs: dict):
    # Backend implementation
    backend_crew = Crew(
        agents=[api_creator_agent, data_model_agent],
        tasks=create_backend_tasks(inputs["crew_assignments"]["backend_plan"]),
        process=Process.sequential,
        verbose=True
    )
    backend_result = backend_crew.kickoff()

    # Web implementation
    web_crew = Crew(
        agents=[dynamic_page_builder_agent],
        tasks=create_web_tasks(inputs["crew_assignments"]["frontend_plan"]),
        process=Process.sequential,
        verbose=True
    )
    web_result = web_crew.kickoff()

    # Mobile implementation
    mobile_crew = Crew(
        agents=[android_ui_agent, ios_ui_agent],
        tasks=create_mobile_tasks(inputs["crew_assignments"]["mobile_plan"]),
        process=Process.sequential,
        verbose=True
    )
    mobile_result = mobile_crew.kickoff()

    # DevOps implementation
    devops_crew = Crew(
        agents=[devops_agent],
        tasks=create_devops_tasks(inputs["crew_assignments"]["deployment_plan"]),
        process=Process.sequential,
        verbose=True
    )
    devops_result = devops_crew.kickoff()

    def extract_outputs(crew_output):
        if crew_output and crew_output.tasks_output:
            return [task_out.raw for task_out in crew_output.tasks_output if task_out is not None and hasattr(task_out, 'raw')]
        return ["Error: No output found for this crew segment."]

    return {
        "backend": extract_outputs(backend_result),
        "web": extract_outputs(web_result),
        "mobile": extract_outputs(mobile_result),
        "devops": extract_outputs(devops_result)
    }

def create_backend_tasks(plan):
    # Convert plan into concrete tasks
    # This is a simplified example. In a real scenario,
    # you'd have a more robust way to create tasks from the plan.
    tasks = []
    if plan and "tasks" in plan and isinstance(plan["tasks"], list):
        for task_desc in plan["tasks"]:
            agent = api_creator_agent if "API" in task_desc else data_model_agent
            tasks.append(
                Task(
                    description=task_desc,
                    agent=agent,
                    expected_output=f"Completed {task_desc}"
                )
            )
    return tasks

def create_web_tasks(plan):
    # Convert plan into concrete tasks
    tasks = []
    if plan and "tasks" in plan and isinstance(plan["tasks"], list):
        for task_desc in plan["tasks"]:
            tasks.append(
                Task(
                    description=task_desc,
                    agent=dynamic_page_builder_agent,
                    expected_output=f"Completed {task_desc}"
                )
            )
    return tasks

def create_mobile_tasks(plan):
    # Convert plan into concrete tasks
    tasks = []
    if plan and "tasks" in plan and isinstance(plan["tasks"], list):
        for task_desc in plan["tasks"]:
            # This is a simplified agent assignment.
            # You might need more sophisticated logic.
            agent = android_ui_agent if "Android" in task_desc else ios_ui_agent
            tasks.append(
                Task(
                    description=task_desc,
                    agent=agent,
                    expected_output=f"Completed {task_desc}"
                )
            )
    return tasks

def create_devops_tasks(plan):
    # Convert plan into concrete tasks
    tasks = []
    if plan and "tasks" in plan and isinstance(plan["tasks"], list):
        for task_desc in plan["tasks"]:
            tasks.append(
                Task(
                    description=task_desc,
                    agent=devops_agent,
                    expected_output=f"Completed {task_desc}"
                )
            )
    return tasks
