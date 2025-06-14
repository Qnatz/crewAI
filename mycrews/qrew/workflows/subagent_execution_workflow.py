from crewai import Crew, Process, Task
from ..agents.backend import api_creator_agent, data_model_agent
from ..agents.web import dynamic_page_builder_agent
from ..agents.mobile import android_ui_agent, ios_ui_agent
from ..agents.devops import devops_agent

def run_subagent_execution_workflow(inputs: dict):
    # Backend implementation
    backend_crew = Crew(
        agents=[api_creator_agent, data_model_agent],
        tasks=create_backend_tasks(inputs["crew_assignment"]["backend_plan"]),
        process=Process.sequential,
        verbose=True
    )
    backend_result = backend_crew.kickoff()

    # Web implementation
    web_crew = Crew(
        agents=[dynamic_page_builder_agent],
        tasks=create_web_tasks(inputs["crew_assignment"]["frontend_plan"]),
        process=Process.sequential,
        verbose=True
    )
    web_result = web_crew.kickoff()

    # Mobile implementation
    mobile_crew = Crew(
        agents=[android_ui_agent, ios_ui_agent],
        tasks=create_mobile_tasks(inputs["crew_assignment"]["mobile_plan"]),
        process=Process.sequential,
        verbose=True
    )
    mobile_result = mobile_crew.kickoff()

    # DevOps implementation
    devops_crew = Crew(
        agents=[devops_agent],
        tasks=create_devops_tasks(inputs["crew_assignment"]["deployment_plan"]),
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
    tasks = []
    if plan and isinstance(plan, dict) and "tasks" in plan and isinstance(plan["tasks"], list) and plan["tasks"]:
        for task_desc in plan["tasks"]:
            if not isinstance(task_desc, str) or not task_desc.strip():
                print(f"Warning: Invalid task description in backend_plan: '{task_desc}'. Skipping.")
                continue
            agent_to_assign = api_creator_agent
            if "model" in task_desc.lower() or "schema" in task_desc.lower() or "database" in task_desc.lower():
                agent_to_assign = data_model_agent
            tasks.append(
                Task(
                    description=task_desc,
                    agent=agent_to_assign,
                    expected_output=f"The actual code/configuration for the backend task: {task_desc}. This should be directly usable code, not a message.",
                    max_retries=1,
                    # TODO: Implement a more robust guardrail (LLM-assisted or functional) for code validation.
                    guardrail=f"Ensure the output is actual code/configuration for task: {task_desc}. Avoid conversational filler."
                )
            )
    else:
        print(f"Warning: No valid tasks found in backend_plan or plan is malformed: {plan}")

    if not tasks: # This print remains for the case where the loop completes but no tasks were valid, or plan["tasks"] was empty
        print(f"Warning: No tasks ultimately created for backend_plan: {plan}")
    return tasks

def create_web_tasks(plan):
    tasks = []
    if plan and isinstance(plan, dict) and "tasks" in plan and isinstance(plan["tasks"], list) and plan["tasks"]:
        for task_desc in plan["tasks"]:
            if not isinstance(task_desc, str) or not task_desc.strip():
                print(f"Warning: Invalid task description in frontend_plan: '{task_desc}'. Skipping.")
                continue
            tasks.append(
                Task(
                    description=task_desc,
                    agent=dynamic_page_builder_agent,
                    expected_output=f"The actual HTML/JS/CSS snippets or component code for the web task: {task_desc}. This should be directly usable code, not a message.",
                    max_retries=1,
                    # TODO: Implement a more robust guardrail (LLM-assisted or functional) for code validation.
                    guardrail=f"Ensure the output is actual code/configuration for task: {task_desc}. Avoid conversational filler."
                )
            )
    else:
        print(f"Warning: No valid tasks found in frontend_plan or plan is malformed: {plan}")

    if not tasks:
        print(f"Warning: No tasks ultimately created for frontend_plan: {plan}")
    return tasks

def create_mobile_tasks(plan):
    tasks = []
    if plan and isinstance(plan, dict) and "tasks" in plan and isinstance(plan["tasks"], list) and plan["tasks"]:
        for task_desc in plan["tasks"]:
            if not isinstance(task_desc, str) or not task_desc.strip():
                print(f"Warning: Invalid task description in mobile_plan: '{task_desc}'. Skipping.")
                continue
            agent_to_assign = android_ui_agent
            if "ios" in task_desc.lower():
                agent_to_assign = ios_ui_agent
            elif "android" in task_desc.lower():
                 agent_to_assign = android_ui_agent
            tasks.append(
                Task(
                    description=task_desc,
                    agent=agent_to_assign,
                    expected_output=f"The actual UI code snippets or platform-specific configurations for the mobile task: {task_desc}. This should be directly usable code, not a message.",
                    max_retries=1,
                    # TODO: Implement a more robust guardrail (LLM-assisted or functional) for code validation.
                    guardrail=f"Ensure the output is actual code/configuration for task: {task_desc}. Avoid conversational filler."
                )
            )
    else:
        print(f"Warning: No valid tasks found in mobile_plan or plan is malformed: {plan}")

    if not tasks:
        print(f"Warning: No tasks ultimately created for mobile_plan: {plan}")
    return tasks

def create_devops_tasks(plan):
    tasks = []
    if plan and isinstance(plan, dict) and "tasks" in plan and isinstance(plan["tasks"], list) and plan["tasks"]:
        for task_desc in plan["tasks"]:
            if not isinstance(task_desc, str) or not task_desc.strip():
                print(f"Warning: Invalid task description in deployment_plan: '{task_desc}'. Skipping.")
                continue
            tasks.append(
                Task(
                    description=task_desc,
                    agent=devops_agent,
                    expected_output=f"The actual script snippets, Dockerfile lines, or config file sections for the devops task: {task_desc}. This should be directly usable code, not a message.",
                    max_retries=1,
                    # TODO: Implement a more robust guardrail (LLM-assisted or functional) for code validation.
                    guardrail=f"Ensure the output is actual code/configuration for task: {task_desc}. Avoid conversational filler."
                )
            )
    else:
        print(f"Warning: No valid tasks found in deployment_plan or plan is malformed: {plan}")

    if not tasks:
        print(f"Warning: No tasks ultimately created for deployment_plan: {plan}")
    return tasks
