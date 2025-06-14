from crewai import Crew, Process, Task
from crewai.tasks.task_output import TaskOutput # Ensure TaskOutput is imported
from typing import Any # Ensure Any is imported
import re # Added import re
from ..agents.backend import api_creator_agent, data_model_agent
from ..agents.web import dynamic_page_builder_agent
from ..agents.mobile import android_ui_agent, ios_ui_agent
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
            description_str = task_desc + " IMPORTANT REMINDER: Your final output for this task must be strictly the code/configuration artifact itself, with absolutely no other surrounding text or explanations, as per the detailed 'expected_output' format."
            expected_output_str = f"CRITICAL: Your entire response MUST be ONLY the raw code/configuration for the task: '{task_desc}'. NO explanations, NO apologies, NO introductory or concluding remarks, NO markdown fences (like ```python or ```), NO conversational text. ONLY the code/configuration itself. For example, if creating a Python function, the output should start with 'def' or 'async def'. If it's a JSON config, it starts with '{{'. If it's HTML, it starts with '<!DOCTYPE html>' or a tag. Adhere strictly to outputting only the required software artifact."
            tasks.append(
                Task(
                    description=description_str,
                    agent=dynamic_page_builder_agent,
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
            agent_to_assign = android_ui_agent
            if "ios" in task_desc.lower():
                agent_to_assign = ios_ui_agent
            elif "android" in task_desc.lower():
                 agent_to_assign = android_ui_agent
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
