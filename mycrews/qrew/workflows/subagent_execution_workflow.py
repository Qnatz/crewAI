from crewai import Crew, Process, Task
from crewai.tasks.task_output import TaskOutput # Ensure TaskOutput is imported
from typing import Any # Ensure Any is imported
import re # Added import re
# Direct imports for specialized backend agents
from ..agents.backend.api_creator_agent.agent import api_creator_agent
from ..agents.backend.data_model_agent.agent import data_model_agent
from ..agents.backend.auth_agent.agent import auth_agent as backend_auth_agent
from ..agents.backend.config_agent.agent import config_agent
from ..agents.backend.queue_agent.agent import queue_agent
from ..agents.backend.storage_agent.agent import storage_agent as backend_storage_agent
from ..agents.backend.sync_agent.agent import sync_agent as backend_sync_agent

# Direct imports for specialized web agents
from ..agents.web.dynamic_page_builder_agent.agent import dynamic_page_builder_agent
from ..agents.web.static_page_builder_agent.agent import static_page_builder_agent
from ..agents.web.asset_manager_agent.agent import asset_manager_agent

# Direct imports for specialized mobile agents from platform-specific subdirectories
from ..agents.mobile.android.android_api_client_agent.agent import android_api_client_agent
from ..agents.mobile.android.android_storage_agent.agent import android_storage_agent
from ..agents.mobile.android.android_ui_agent.agent import android_ui_agent
from ..agents.mobile.ios.ios_api_client_agent.agent import ios_api_client_agent
from ..agents.mobile.ios.ios_storage_agent.agent import ios_storage_agent
from ..agents.mobile.ios.ios_ui_agent.agent import ios_ui_agent

from ..agents.devops import devops_agent

def validate_and_extract_code_output(task_output: TaskOutput) -> tuple[bool, Any]:
    try:
        if not hasattr(task_output, 'raw') or not isinstance(task_output.raw, str):
            print("GUARDRAIL_CODE_EXTRACT: Input task_output.raw is not a string or not present.")
            return False, "Guardrail input (task_output.raw) must be a string and present."

        output_str = task_output.raw.strip()
        print(f"GUARDRAIL_CODE_EXTRACT: Original output (first 300 chars): '{output_str[:300]}'")

        extracted_code_blocks = []

        # Regex to find common fenced code blocks (non-greedy)
        # Matches ```optional_lang
    #...code...
    #``` or ```...code...```
        fence_patterns = [
            re.compile(r"```(?:[a-zA-Z0-9_]+)?\s*\n(.*?)\n```", re.DOTALL), # For multi-line blocks with language
            re.compile(r"```(.*?)```", re.DOTALL) # For single or multi-line blocks without explicit language
        ]

        temp_output_str = output_str
        for pattern in fence_patterns:
            matches = pattern.findall(temp_output_str)
            if matches:
                for match in matches:
                    extracted_code_blocks.append(match.strip())
                # Remove found blocks to avoid re-matching if there are multiple types of fences
                temp_output_str = pattern.sub("", temp_output_str).strip()

        final_extracted_code = ""
        if extracted_code_blocks:
            final_extracted_code = "\n\n".join(extracted_code_blocks).strip()
            print(f"GUARDRAIL_CODE_EXTRACT: Extracted code using fences (first 300 chars): '{final_extracted_code[:300]}'")
        else:
            # Fallback: If no fences, assume the whole (or significant part of) string might be code if it's not conversational.
            # This is a basic heuristic: if it's short and mostly plain language, it's probably not just code.
            # A more sophisticated check might involve token counting, keyword density, etc.
            # For now, if it didn't have fences, we'll take it as is but check if it's empty.
            # The hyper-focused prompts are meant to minimize conversational text.
            if len(output_str.split()) > 50 and len(re.findall(r'[;,=\{\}\[\]\(\)<>]', output_str)) < 5: # Heuristic: many words, few code symbols
                 print(f"GUARDRAIL_CODE_EXTRACT: No fences found, and output looks more like text than code. Length: {len(output_str.split())} words.")
                 # Previously, the error was "The task result does not solely provide code/configuration examples... It includes significant explanatory text"
                 # This guardrail should now return the extracted code. If nothing is extracted and the original output is verbose, it should fail.
                 return False, "Output appears to be mainly explanatory text without clear code blocks, or code is not properly fenced."
            final_extracted_code = output_str # Take the whole string if no fences and it's not clearly verbose text
            print(f"GUARDRAIL_CODE_EXTRACT: No fences found. Assuming entire content might be code/config (first 300 chars): '{final_extracted_code[:300]}'")


        if not final_extracted_code:
            print("GUARDRAIL_CODE_EXTRACT: No code content could be extracted.")
            return False, "No code/configuration content could be extracted from the output."

        # At this point, final_extracted_code contains the best effort extraction.
        # The previous error message was: "The task result does not solely provide code/configuration examples... It includes significant explanatory text..."
        # This guardrail's purpose is to *extract* the code. If successful, it returns (True, extracted_code).
        # The external guardrail (if CrewAI applies another one based on the string) would then judge this *extracted_code*.
        # For a functional guardrail, we decide here.
        # Let's refine the condition for success: extracted code should be substantial.
        if len(final_extracted_code) < 10 and not ("def" in final_extracted_code or "class" in final_extracted_code or "{" in final_extracted_code or "<" in final_extracted_code): # very short, not looking like code
             print(f"GUARDRAIL_CODE_EXTRACT: Extracted content is very short and doesn't resemble typical code structures: '{final_extracted_code}'")
             return False, f"Extracted content is too short or doesn't resemble code: '{final_extracted_code}'"

        print(f"GUARDRAIL_CODE_EXTRACT: Successfully extracted code/configuration. Length: {len(final_extracted_code)}")
        return True, final_extracted_code # Return the extracted code
    except Exception as e:
        print(f"GUARDRAIL_CODE_EXTRACT: Error during code extraction: {str(e)}")
        return False, f"Error during guardrail code extraction: {str(e)}"

def run_subagent_execution_workflow(inputs: dict):
    print(f"DEBUG: Entering run_subagent_execution_workflow with inputs: {inputs.get('project_name', 'N/A')}") # Scope not easily available here
    # Backend implementation
    backend_tasks = create_backend_tasks(inputs["crew_assignment"]["backend_plan"])
    if backend_tasks:
        # Ensure all specialized backend agents are available to the crew
        all_backend_agents = [
            api_creator_agent,
            data_model_agent,
            backend_auth_agent,
            config_agent,
            queue_agent,
            backend_storage_agent,
            backend_sync_agent
        ]
        backend_crew = Crew(
            agents=list(set(all_backend_agents)), # Use set to avoid duplicates if any agent is listed multiple times
            tasks=backend_tasks,
            process=Process.sequential,
            verbose=True
        )
        backend_result = backend_crew.kickoff()
    else:
        backend_result = None
        print("Skipping backend_crew execution as no tasks were generated.")

    # Web implementation
    web_tasks = create_web_tasks(inputs["crew_assignment"]["frontend_plan"])
    if web_tasks:
        all_web_agents = [
            dynamic_page_builder_agent,
            static_page_builder_agent,
            asset_manager_agent
        ]
        web_crew = Crew(
            agents=list(set(all_web_agents)),
            tasks=web_tasks,
            process=Process.sequential,
            verbose=True
        )
        web_result = web_crew.kickoff()
    else:
        web_result = None
        print("Skipping web_crew execution as no tasks were generated.")

    # Mobile implementation
    mobile_tasks = create_mobile_tasks(inputs["crew_assignment"]["mobile_plan"])
    if mobile_tasks:
        all_mobile_agents = [
            android_ui_agent,
            ios_ui_agent,
            android_api_client_agent,
            ios_api_client_agent,
            android_storage_agent,
            ios_storage_agent
        ]
        mobile_crew = Crew(
            agents=list(set(all_mobile_agents)),
            tasks=mobile_tasks,
            process=Process.sequential,
            verbose=True
        )
        mobile_result = mobile_crew.kickoff()
    else:
        mobile_result = None
        print("Skipping mobile_crew execution as no tasks were generated.")

    # DevOps implementation
    devops_tasks = create_devops_tasks(inputs["crew_assignment"]["deployment_plan"])
    if devops_tasks:
        devops_crew = Crew(
            agents=[devops_agent],
            tasks=devops_tasks,
            process=Process.sequential,
            verbose=True
        )
        devops_result = devops_crew.kickoff()
    else:
        devops_result = None
        print("Skipping devops_crew execution as no tasks were generated.")

    # from crewai.tasks.task_output import TaskOutput # Repeated here for clarity in subtask, ensure it's at file top

    def extract_outputs(crew_output):
        if crew_output and hasattr(crew_output, 'tasks_output') and crew_output.tasks_output:
            # Filter out None task_out objects more carefully
            raw_outputs = []
            for task_out in crew_output.tasks_output:
                if task_out is not None and hasattr(task_out, 'raw') and task_out.raw is not None: # Check .raw is not None
                    raw_outputs.append(task_out.raw)
                elif task_out is not None and (not hasattr(task_out, 'raw') or task_out.raw is None): # .raw missing or None
                    # If task_out exists but .raw is missing/None, it might be an error or different structure
                    raw_outputs.append(f"Warning: Task output found but '.raw' attribute missing or None. Task description: '{getattr(task_out, 'description', 'N/A')}'")

            if not raw_outputs and crew_output.tasks_output: # tasks_output was not empty, but all .raw were None/missing or empty strings if .strip() was used
                 return ["Warning: Tasks were present but yielded no processable raw output or failed internally."]
            # If raw_outputs is empty after processing, it means no valid .raw content was found.
            return raw_outputs if raw_outputs else ["Info: No raw output content found in completed tasks for this segment."]

        elif crew_output is None:
            return ["Info: No tasks were executed for this segment as the plan was empty."]

        # This case handles if crew_output is not None, but doesn't have tasks_output or it's empty.
        return ["Info: No tasks were run or no valid crew output for this segment."]

    return {
        "backend": extract_outputs(backend_result),
        "web": extract_outputs(web_result),
        "mobile": extract_outputs(mobile_result),
        "devops": extract_outputs(devops_result)
    }
    print(f"DEBUG: Exiting run_subagent_execution_workflow") # Added exit print before the final return

def create_backend_tasks(plan):
    tasks = []
    if plan and isinstance(plan, dict) and "tasks" in plan and isinstance(plan["tasks"], list) and plan["tasks"]:
        for task_desc in plan["tasks"]:
            if not isinstance(task_desc, str) or not task_desc.strip():
                print(f"Warning: Invalid task description in backend_plan: '{task_desc}'. Skipping.")
                continue

            task_desc_lower = task_desc.lower()
            agent_to_assign = api_creator_agent # Default agent

            if "data model" in task_desc_lower or "schema" in task_desc_lower or "database design" in task_desc_lower:
                agent_to_assign = data_model_agent
            elif "auth" in task_desc_lower or "authentication" in task_desc_lower or "user login" in task_desc_lower or "security policy" in task_desc_lower:
                agent_to_assign = backend_auth_agent
            elif "config" in task_desc_lower or "service setup" in task_desc_lower or "environment variable" in task_desc_lower:
                agent_to_assign = config_agent
            elif "queue" in task_desc_lower or "message broker" in task_desc_lower or "async task" in task_desc_lower:
                agent_to_assign = queue_agent
            elif "storage" in task_desc_lower or "file system" in task_desc_lower or "s3 bucket" in task_desc_lower or "database interaction" in task_desc_lower:
                agent_to_assign = backend_storage_agent
            elif "sync" in task_desc_lower or "data synchronization" in task_desc_lower:
                agent_to_assign = backend_sync_agent
            elif "api" in task_desc_lower or "endpoint" in task_desc_lower or "route" in task_desc_lower:
                agent_to_assign = api_creator_agent
            else:
                print(f"Warning: No specific backend agent matched for task: '{task_desc}'. Defaulting to api_creator_agent.")

            description_str = task_desc + " IMPORTANT REMINDER: Your final output for this task must be strictly the code/configuration artifact itself, with absolutely no other surrounding text or explanations, as per the detailed 'expected_output' format."
            expected_output_str = f"CRITICAL: Your entire response MUST be ONLY the raw code/configuration for the task: '{task_desc}'. NO explanations, NO apologies, NO introductory or concluding remarks, NO markdown fences (like ```python or ```), NO conversational text. ONLY the code/configuration itself. For example, if creating a Python function, the output should start with 'def' or 'async def'. If it's a JSON config, it starts with '{{'. If it's HTML, it starts with '<!DOCTYPE html>' or a tag. Adhere strictly to outputting only the required software artifact."
            tasks.append(
                Task(
                    description=description_str,
                    agent=agent_to_assign,
                    expected_output=expected_output_str,
                    max_retries=1,
                    guardrail=validate_and_extract_code_output
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

            task_desc_lower = task_desc.lower()
            agent_to_assign = dynamic_page_builder_agent # Default

            if "static page" in task_desc_lower or \
               ("info page" in task_desc_lower or "html page" in task_desc_lower) and not "dynamic" in task_desc_lower:
                agent_to_assign = static_page_builder_agent
            elif ("asset" in task_desc_lower or "image" in task_desc_lower or \
                  "css" in task_desc_lower or "javascript file" in task_desc_lower) or \
                 ("optimize" in task_desc_lower and "asset" in task_desc_lower):
                agent_to_assign = asset_manager_agent
            elif "dynamic" in task_desc_lower or "interactive" in task_desc_lower or \
                 "component" in task_desc_lower or "feature" in task_desc_lower:
                agent_to_assign = dynamic_page_builder_agent
            else:
                print(f"Warning: No specific web agent matched for task: '{task_desc}'. Defaulting to dynamic_page_builder_agent.")

            description_str = task_desc + " IMPORTANT REMINDER: Your final output for this task must be strictly the code/configuration artifact itself, with absolutely no other surrounding text or explanations, as per the detailed 'expected_output' format."
            expected_output_str = f"CRITICAL: Your entire response MUST be ONLY the raw code/configuration for the task: '{task_desc}'. NO explanations, NO apologies, NO introductory or concluding remarks, NO markdown fences (like ```python or ```), NO conversational text. ONLY the code/configuration itself. For example, if creating a Python function, the output should start with 'def' or 'async def'. If it's a JSON config, it starts with '{{'. If it's HTML, it starts with '<!DOCTYPE html>' or a tag. Adhere strictly to outputting only the required software artifact."
            tasks.append(
                Task(
                    description=description_str,
                    agent=agent_to_assign,
                    expected_output=expected_output_str,
                    max_retries=1,
                    guardrail=validate_and_extract_code_output
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

            task_desc_lower = task_desc.lower()
            agent_to_assign = None

            is_android = "android" in task_desc_lower
            is_ios = "ios" in task_desc_lower or "apple" in task_desc_lower

            if "api client" in task_desc_lower or "network request" in task_desc_lower or "fetch data" in task_desc_lower:
                if is_android:
                    agent_to_assign = android_api_client_agent
                elif is_ios:
                    agent_to_assign = ios_api_client_agent
                # else: Consider a generic mobile api client or default if platform is not specified but task is API related
            elif "storage" in task_desc_lower or "database" in task_desc_lower or "local data" in task_desc_lower:
                if is_android:
                    agent_to_assign = android_storage_agent
                elif is_ios:
                    agent_to_assign = ios_storage_agent
                # else: Consider a generic mobile storage agent
            elif "ui" in task_desc_lower or "screen" in task_desc_lower or "layout" in task_desc_lower:
                if is_android:
                    agent_to_assign = android_ui_agent
                elif is_ios:
                    agent_to_assign = ios_ui_agent

            if agent_to_assign is None: # Fallback if no specific category matches or platform ambiguity for specialized tasks
                if is_android:
                    agent_to_assign = android_ui_agent # Default Android to UI agent
                elif is_ios:
                    agent_to_assign = ios_ui_agent # Default iOS to UI agent
                else:
                    # If no platform is specified, default to Android UI agent and log a warning.
                    # This could be made more sophisticated, e.g. by having a generic mobile agent
                    # or by requiring platform specification in task descriptions.
                    agent_to_assign = android_ui_agent
                    print(f"Warning: No specific mobile agent category or platform matched for task: '{task_desc}'. Defaulting to android_ui_agent.")

            description_str = task_desc + " IMPORTANT REMINDER: Your final output for this task must be strictly the code/configuration artifact itself, with absolutely no other surrounding text or explanations, as per the detailed 'expected_output' format."
            expected_output_str = f"CRITICAL: Your entire response MUST be ONLY the raw code/configuration for the task: '{task_desc}'. NO explanations, NO apologies, NO introductory or concluding remarks, NO markdown fences (like ```python or ```), NO conversational text. ONLY the code/configuration itself. For example, if creating a Python function, the output should start with 'def' or 'async def'. If it's a JSON config, it starts with '{{'. If it's HTML, it starts with '<!DOCTYPE html>' or a tag. Adhere strictly to outputting only the required software artifact."
            tasks.append(
                Task(
                    description=description_str,
                    agent=agent_to_assign,
                    expected_output=expected_output_str,
                    max_retries=1,
                    guardrail=validate_and_extract_code_output
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
            description_str = task_desc + " IMPORTANT REMINDER: Your final output for this task must be strictly the code/configuration artifact itself, with absolutely no other surrounding text or explanations, as per the detailed 'expected_output' format."
            expected_output_str = f"CRITICAL: Your entire response MUST be ONLY the raw code/configuration for the task: '{task_desc}'. NO explanations, NO apologies, NO introductory or concluding remarks, NO markdown fences (like ```python or ```), NO conversational text. ONLY the code/configuration itself. For example, if creating a Python function, the output should start with 'def' or 'async def'. If it's a JSON config, it starts with '{{'. If it's HTML, it starts with '<!DOCTYPE html>' or a tag. Adhere strictly to outputting only the required software artifact."
            tasks.append(
                Task(
                    description=description_str,
                    agent=devops_agent,
                    expected_output=expected_output_str,
                    max_retries=1,
                    guardrail=validate_and_extract_code_output
                )
            )
    else:
        print(f"Warning: No valid tasks found in deployment_plan or plan is malformed: {plan}")

    if not tasks:
        print(f"Warning: No tasks ultimately created for deployment_plan: {plan}")
    return tasks
