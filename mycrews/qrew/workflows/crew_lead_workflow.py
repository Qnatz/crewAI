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
            expected_output="A JSON object with a single key 'tasks'. The value of 'tasks' MUST be a list of strings, where each string is a detailed task description for backend development. Ensure the output is ONLY the JSON object itself, starting with { and ending with }."
        ),
        Task(
            description=f"Plan frontend implementation for {inputs['project_name']}. "                         f"The overall project architecture summary is: {architecture_summary_str}",
            agent=web_lead,
            expected_output="A JSON object with a single key 'tasks'. The value of 'tasks' MUST be a list of strings, where each string is a detailed task description for frontend implementation. Ensure the output is ONLY the JSON object itself, starting with { and ending with }."
        ),
        Task(
            description=f"Plan mobile implementation for {inputs['project_name']}. "                         f"The overall project architecture summary is: {architecture_summary_str}",
            agent=mobile_lead,
            expected_output="A JSON object with a single key 'tasks'. The value of 'tasks' MUST be a list of strings, where each string is a detailed task description for mobile implementation. Ensure the output is ONLY the JSON object itself, starting with { and ending with }."
        ),
        Task(
            description=f"Plan deployment for {inputs['project_name']}. "                         f"The overall project architecture summary is: {architecture_summary_str}",
            agent=devops_lead,
            expected_output="A JSON object with a single key 'tasks'. The value of 'tasks' MUST be a list of strings, where each string is a detailed task description for the deployment plan. Ensure the output is ONLY the JSON object itself, starting with { and ending with }."
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
    default_error_plan = {"tasks": ["Error: Failed to parse plan from LLM output or previous error occurred."]}

    if result and result.tasks_output:
        for i in range(4): # Assuming 4 tasks corresponding to backend, frontend, mobile, devops
            plan_name = ["Backend", "Frontend", "Mobile", "Deployment"][i]
            if i < len(result.tasks_output) and hasattr(result.tasks_output[i], 'raw') and result.tasks_output[i].raw:
                raw_output_str = result.tasks_output[i].raw
                # Attempt to strip markdown fences if present, as LLMs sometimes add them
                if raw_output_str.startswith("```json"):
                    raw_output_str = raw_output_str[len("```json"):].strip()
                    if raw_output_str.endswith("```"):
                        raw_output_str = raw_output_str[:-len("```")].strip()
                elif raw_output_str.startswith("```"):
                     raw_output_str = raw_output_str[len("```"):].strip()
                     if raw_output_str.endswith("```"):
                        raw_output_str = raw_output_str[:-len("```")].strip()

                # Ensure the string starts with { and ends with } after stripping
                if not (raw_output_str.startswith('{') and raw_output_str.endswith('}')):
                    print(f"Warning: Output for {plan_name} plan doesn't look like a JSON object after stripping fences: {raw_output_str[:100]}...") # Log a snippet
                    parsed_outputs.append(default_error_plan)
                    continue

                try:
                    parsed_plan = json.loads(raw_output_str)
                    if not isinstance(parsed_plan, dict) or "tasks" not in parsed_plan or not isinstance(parsed_plan["tasks"], list):
                        print(f"Warning: Parsed JSON for {plan_name} plan is not in the expected format (dict with 'tasks' list): {parsed_plan}")
                        parsed_outputs.append(default_error_plan)
                    else:
                        parsed_outputs.append(parsed_plan)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON for {plan_name} plan: {e}. Raw output: {raw_output_str}")
                    parsed_outputs.append(default_error_plan)
            else:
                parsed_outputs.append({"tasks": [f"Error: {plan_name} task output not found, .raw attribute missing, or raw output is empty."]})
    else: # Fill with error defaults if no tasks_output
        for _ in range(4):
            parsed_outputs.append(default_error_plan)

    # Ensure we have 4 elements in parsed_outputs, even if they are error objects
    while len(parsed_outputs) < 4:
        parsed_outputs.append(default_error_plan)

    return {
        "backend_plan": parsed_outputs[0],
        "frontend_plan": parsed_outputs[1],
        "mobile_plan": parsed_outputs[2],
        "deployment_plan": parsed_outputs[3]
    }
