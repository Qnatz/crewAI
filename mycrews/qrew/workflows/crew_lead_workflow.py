import json
from typing import Any # Added Any
from crewai import Crew, Process, Task
from crewai.tasks.task_output import TaskOutput # Added
from ..lead_agents.backend_project_coordinator_agent.agent import backend_project_coordinator_agent
from ..lead_agents.web_project_coordinator_agent.agent import web_project_coordinator_agent
from ..lead_agents.mobile_project_coordinator_agent.agent import mobile_project_coordinator_agent
from ..lead_agents.devops_and_integration_coordinator_agent.agent import devops_and_integration_coordinator_agent

def validate_json_plan_output(task_output: TaskOutput) -> tuple[bool, Any]:
    """
    Validates if the LLM output (from task_output.raw) is a JSON object
    with a 'tasks' key containing a list.
    """
    if not hasattr(task_output, 'raw') or not isinstance(task_output.raw, str):
        return False, "Guardrail input (task_output.raw) must be a string and present."
    output_str = task_output.raw

    # Strip markdown fences if present
    if output_str.startswith("```json"):
        output_str = output_str[len("```json"):].strip()
        if output_str.endswith("```"):
            output_str = output_str[:-len("```")].strip()
    elif output_str.startswith("```"):
        output_str = output_str[len("```"):].strip()
        if output_str.endswith("```"):
            output_str = output_str[:-len("```")].strip()

    # Ensure the string starts with { and ends with } after stripping, if it's not empty
    # This is a gentle correction, as json.loads() will fail anyway if it's not a valid object/array start/end.
    # However, LLMs sometimes forget the final brace after stripping.
    # This specific check might be too aggressive or not needed if json.loads() is the ultimate validator.
    # For now, let's rely on the stripping and then the json.loads() to do its job.
    # An empty string after stripping should also fail json.loads() correctly.

    try:
        data = json.loads(output_str)
        if isinstance(data, dict) and "tasks" in data and isinstance(data["tasks"], list):
            # Further check if all tasks in the list are strings, as per original intent
            if all(isinstance(task_item, str) for task_item in data["tasks"]):
                return True, data
            else:
                return False, "All items in the 'tasks' list must be strings."
        else:
            return False, "Output must be a valid JSON object with a 'tasks' key containing a list of strings."
    except json.JSONDecodeError:
        return False, "Output must be valid JSON." # output_str implied
    except Exception as e: # Catch any other unexpected errors during validation
        return False, f"Validation error: {str(e)}"


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
            description=f"Plan backend implementation for {inputs['project_name']}. " \
                        f"The overall project architecture summary is: {architecture_summary_str}. " \
                        f"The architecture document now includes detailed component breakdowns, API endpoint definitions, and database schemas. Use these to create highly specific tasks, e.g., 'Implement GET /api/v1/items endpoint as per spec X with data model Y'.",
            agent=backend_lead,
            expected_output="A valid JSON object with a single key 'tasks'. The value of 'tasks' MUST be a list of strings, where each string is a detailed task description. Ensure the output is ONLY the JSON object itself, starting with { and ending with }.",
            guardrail=validate_json_plan_output,
            max_retries=2
        ),
        Task(
            description=f"Plan frontend implementation for {inputs['project_name']}. " \
                        f"The overall project architecture summary is: {architecture_summary_str}. " \
                        f"The architecture document provides detailed components and their API dependencies. Use this to define tasks for UI views, component creation, and API integrations, e.g., 'Develop UserProfile view to display data from /users/me endpoint'.",
            agent=web_lead,
            expected_output="CRITICAL: Your output MUST be a valid JSON object and NOTHING ELSE. It must start with '{' and end with '}'. Do not include any explanatory text, markdown code fences (like ```json or ```), or any characters outside of the JSON object itself. The JSON object must have a single key 'tasks', and its value must be a list of strings, where each string is a detailed task description for frontend implementation.",
            guardrail=validate_json_plan_output,
            max_retries=2
        ),
        Task(
            description=f"Plan mobile implementation for {inputs['project_name']}. " \
                        f"The overall project architecture summary is: {architecture_summary_str}. " \
                        f"Refer to the detailed components and API specifications. Create tasks for specific screens, platform-specific UI elements, and API data consumption, e.g., 'Implement iOS ItemDetail screen using data from /items/{{item_id}}'.",
            agent=mobile_lead,
            expected_output="A valid JSON object with a single key 'tasks'. The value of 'tasks' MUST be a list of strings, where each string is a detailed task description. Ensure the output is ONLY the JSON object itself, starting with { and ending with }.",
            guardrail=validate_json_plan_output,
            max_retries=2
        ),
        Task(
            description=f"Plan deployment for {inputs['project_name']}. " \
                        f"The overall project architecture summary is: {architecture_summary_str}. " \
                        f"The architecture details specific components and the database schema. Plan tasks for deploying each service, setting up the database tables, and configuring CI/CD pipelines, e.g., 'Configure PostgreSQL Users table based on schema' or 'Create Dockerfile for UserManagementService'.",
            agent=devops_lead,
            expected_output="A valid JSON object with a single key 'tasks'. The value of 'tasks' MUST be a list of strings, where each string is a detailed task description. Ensure the output is ONLY the JSON object itself, starting with { and ending with }.",
            guardrail=validate_json_plan_output,
            max_retries=2
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

    parsed_outputs = []
    default_error_plan = {"tasks": ["Error: Failed to generate a valid plan even after retries, or an unexpected error occurred."]}

    if result and result.tasks_output:
        for i in range(len(tasks)): # Iterate based on the number of tasks defined
            task_output = result.tasks_output[i] if i < len(result.tasks_output) else None
            plan_name = ["Backend", "Frontend", "Mobile", "Deployment"][i] # Assuming order

            if task_output and hasattr(task_output, 'raw') and task_output.raw:
                # The guardrail should ensure task_output.raw is a valid JSON string.
                # If the task failed despite retries, task_output.raw might be None or reflect an error state,
                # or the task itself might be marked as failed (not directly checked here, relying on output).
                try:
                    # The guardrail already validated and returned the parsed data if successful.
                    # However, crewAI's TaskOutput currently puts the raw string in .raw.
                    # If the guardrail passed, .raw should be the valid JSON string.
                    # If the task failed after retries with guardrail, .raw might be the last failing output
                    # or an error message from crewAI. The guardrail's role is to prevent bad data *before* this point.

                    # We attempt to parse what's in .raw. If it's valid JSON (meaning guardrail worked or last attempt was good), we use it.
                    # If it's not (meaning guardrail failed on last attempt and crewAI passed it through, or some other issue),
                    # we fall back to default_error_plan.
                    parsed_plan = json.loads(task_output.raw)

                    # Double-check format, though guardrail should have caught this.
                    if isinstance(parsed_plan, dict) and "tasks" in parsed_plan and isinstance(parsed_plan["tasks"], list):
                        parsed_outputs.append(parsed_plan)
                    else:
                        print(f"Warning: Output for {plan_name} plan was not in the expected format despite guardrail. Raw: {task_output.raw}")
                        parsed_outputs.append(default_error_plan)
                except json.JSONDecodeError:
                    # This case implies the guardrail might have failed on its last attempt and crewAI returned
                    # the raw, unvalidated output, or the task failed fundamentally.
                    print(f"Error: Failed to parse JSON for {plan_name} plan from task's raw output, even after guardrail and retries. Raw: {task_output.raw}")
                    parsed_outputs.append(default_error_plan)
            else:
                # This means the task either failed to produce any raw output, or the task_output object itself is missing.
                print(f"Error: No valid output found for {plan_name} plan after task execution (possibly due to max_retries reached or other critical error).")
                parsed_outputs.append(default_error_plan)
    else:
        # This case handles if crew.kickoff() returned None or result.tasks_output is empty.
        print("Error: Crew execution did not produce any task outputs.")
        for _ in range(len(tasks)): # Use length of tasks array
            parsed_outputs.append(default_error_plan)

    # Ensure we have an entry for each plan, even if it's an error object.
    # This is more robust if the number of tasks changes, though plan_names are hardcoded.
    expected_num_outputs = len(tasks)
    while len(parsed_outputs) < expected_num_outputs:
        print(f"Warning: Missing an expected output, padding with default error plan. Expected {expected_num_outputs}, got {len(parsed_outputs)}")
        parsed_outputs.append(default_error_plan)

    # Ensure we don't exceed the expected number of outputs if something went wrong with loop logic
    parsed_outputs = parsed_outputs[:expected_num_outputs]


    return {
        "backend_plan": parsed_outputs[0] if len(parsed_outputs) > 0 else default_error_plan,
        "frontend_plan": parsed_outputs[1] if len(parsed_outputs) > 1 else default_error_plan,
        "mobile_plan": parsed_outputs[2] if len(parsed_outputs) > 2 else default_error_plan,
        "deployment_plan": parsed_outputs[3] if len(parsed_outputs) > 3 else default_error_plan
    }
