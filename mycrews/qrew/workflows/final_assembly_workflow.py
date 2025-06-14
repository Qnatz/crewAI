import json
import re # Added
from typing import Any # Added
from crewai import Crew, Process, Task
from crewai.tasks.task_output import TaskOutput # Added
from ..orchestrators.final_assembler_agent.agent import final_assembler_agent
from ..agents.dev_utilities import code_writer_agent
from ..agents.dev_utilities import debugger_agent as error_handler_agent

def validate_readiness_report(task_output: TaskOutput) -> tuple[bool, Any]:
    if not hasattr(task_output, 'raw') or not isinstance(task_output.raw, str):
        print("GUARDRAIL_READINESS_REPORT: Input task_output.raw is not a string or not present.")
        return False, "Guardrail input (task_output.raw) must be a string and present."

    output_str = task_output.raw.strip()
    print(f"GUARDRAIL_READINESS_REPORT: Validating output (first 300 chars): '{output_str[:300]}'")

    cleaned_output = output_str.lower()

    # Keywords indicating a valid assessment was made (even if it finds errors)
    assessment_keywords = [
        "readiness assessment", "error report", "integration readiness",
        "component analysis", "issues found", "vulnerabilities found",
        "components ready", "system verified", "verification complete"
    ]

    # Keywords indicating a valid report about missing data
    missing_data_keywords = [
        "cannot perform assessment", "missing component data", "input data lacking",
        "unable to assess", "components not provided", "component details from subagent execution"
        # Added the specific phrase from the new prompt
    ]

    is_valid_assessment = any(keyword in cleaned_output for keyword in assessment_keywords)
    is_valid_missing_data_report = any(keyword in cleaned_output for keyword in missing_data_keywords)

    if is_valid_assessment:
        if len(output_str) < 50: # Too short for a "comprehensive" assessment
            print("GUARDRAIL_READINESS_REPORT: Output claims assessment but is too short.")
            return False, "Assessment report is too brief to be considered comprehensive."
        print("GUARDRAIL_READINESS_REPORT: Valid assessment report detected.")
        return True, task_output.raw # Return original raw output

    if is_valid_missing_data_report:
        if len(output_str) < 30: # Too short for a clear statement about missing data
            print("GUARDRAIL_READINESS_REPORT: Output claims missing data but statement is too short.")
            return False, "Statement about missing data is too brief."
        print("GUARDRAIL_READINESS_REPORT: Valid report about missing data detected.")
        return True, task_output.raw # Return original raw output

    print("GUARDRAIL_READINESS_REPORT: Output does not seem to be a valid assessment or a clear missing data report.")
    return False, "Output is neither a readiness assessment/error report nor a clear statement about missing input components."

def validate_integration_plan_output(task_output: TaskOutput) -> tuple[bool, Any]:
    if not hasattr(task_output, 'raw') or not isinstance(task_output.raw, str):
        print("GUARDRAIL_INTEGRATION_PLAN: Input task_output.raw is not a string or not present.")
        return False, "Guardrail input (task_output.raw) must be a string and present."

    output_str = task_output.raw.strip()
    print(f"GUARDRAIL_INTEGRATION_PLAN: Validating output (first 300 chars): '{output_str[:300]}'")

    if not output_str: # Handle empty string after strip
        print("GUARDRAIL_INTEGRATION_PLAN: Output is empty.")
        return False, "Output is empty after stripping whitespace."

    cleaned_output_lower = output_str.lower()

    # Keywords indicating a planning effort
    plan_keywords = [
        "integration plan", "integration steps", "sequence of integration",
        "component interaction", "data flow", "configuration management",
        "testing strategy", "deployment considerations", "deployment sequence"
    ]

    # Keywords indicating acknowledgment of issues within a plan
    issue_keywords = [
        "blockers", "prerequisites", "missing information", "non-functional",
        "resolve them", "address these issues", "contingency"
    ]

    # Check for presence of planning content
    has_plan_content = any(keyword in cleaned_output_lower for keyword in plan_keywords)

    # Check for acknowledgment of issues (which is acceptable if a plan is also present)
    has_issue_discussion = any(keyword in cleaned_output_lower for keyword in issue_keywords)

    # Heuristic: Substantial length suggests more than just a simple refusal.
    is_substantial = len(output_str) > 150 # Arbitrary length, tune if needed

    # Condition for passing:
    # 1. Must have planning content.
    # 2. Must be of substantial length.
    # (It's okay if it also discusses issues/blockers).
    if has_plan_content and is_substantial:
        print("GUARDRAIL_INTEGRATION_PLAN: Output appears to be a substantive integration plan.")
        return True, task_output.raw # Return original raw output

    # If it mentions issues but has no plan content or isn't substantial
    if has_issue_discussion and not has_plan_content and not is_substantial:
        print("GUARDRAIL_INTEGRATION_PLAN: Output primarily discusses issues without sufficient planning content or detail.")
        return False, "Output focuses on issues without providing a sufficient integration plan for available components or clear steps to resolve."

    # If it has neither, or is too short.
    print("GUARDRAIL_INTEGRATION_PLAN: Output lacks clear planning content or sufficient detail.")
    return False, "Output does not contain sufficient elements of an integration plan or is too brief."

def run_final_assembly_workflow(inputs: dict):
    components_summary_str = json.dumps(inputs.get("subagent_execution", {}), indent=2) # Corrected key
    architecture_summary_str = json.dumps(inputs.get("architecture", {}), indent=2)

    # Error checking phase
    error_check_task = Task(
        description=f"Verify all components provided in the summary for integration readiness: '{components_summary_str}'. CRUCIAL: If the component summary is empty or indicates no components (e.g., '{{}}', '[]'), your output MUST clearly state that a readiness assessment cannot be performed due to missing 'component details from subagent execution' and what was expected (a summary of components). Do NOT describe hypothetical procedures you would follow if data were present. If components ARE provided (the summary is not empty), produce a detailed error report and readiness assessment for them, identifying any issues or confirming their readiness.",
        agent=error_handler_agent,
        expected_output="A comprehensive error report and readiness assessment for the provided components. OR, if component data was missing as indicated by an empty input summary (e.g., '{{}}', '[]'), the output MUST be a clear statement specifically indicating that 'Readiness assessment cannot be performed due to missing component details from subagent execution.' This statement must be direct and not include hypothetical procedures.",
        max_retries=1,
        guardrail=validate_readiness_report
    )

    # Integration planning
    integration_task = Task(
        description=f"Create a detailed integration plan based on the available components summarized as: {components_summary_str}. The overall project architecture is: {architecture_summary_str}. Your goal is to outline how these components should be combined into a functional system. IMPORTANT: If the component summary or architecture indicates some components are non-functional, incomplete, or if crucial information is missing, your integration plan MUST still be as complete as possible for the *available and functional* parts. Clearly identify any non-functional components or missing information as 'Blockers' or 'Prerequisites for Full Integration' within a dedicated section of your plan. Also, outline steps or strategies to address these blockers. Do NOT simply state you cannot create a plan. Provide a plan for what is possible now and what is needed to make the rest possible.",
        agent=final_assembler_agent,
        expected_output="A detailed integration plan (Markdown format preferred). The plan MUST include: 1. An explicit 'Integration Sequence' for available/functional components. 2. Details on 'Component Interactions & Data Flow'. 3. 'Configuration Management' notes for integration. 4. A dedicated section: 'Blockers & Prerequisites for Full Integration', which lists non-functional components or missing info and proposes steps/strategies to resolve them. 5. A 'Testing Strategy' for the integrated parts. 6. 'Deployment Considerations' for the integrated system. The plan should be actionable even if some parts are blocked, by clearly separating what can be done from what needs fixing.",
        max_retries=1,
        guardrail=validate_integration_plan_output
    )

    # Code generation
    code_gen_task = Task(
        description=f"Generate final integrated codebase. "                     f"The overall project architecture is: {architecture_summary_str}. "                     f"The components to use for generation are: {components_summary_str}",
        agent=code_writer_agent,
        expected_output="Complete, runnable codebase",
        max_retries=1,
        # TODO: Implement a more robust (LLM-assisted or functional) guardrail to validate code structure and completeness.
        guardrail="Ensure the output consists of a complete codebase based on the integration plan and component specifications. It should contain actual code structures, not just descriptive text."
    )

    # Execute final assembly
    crew = Crew(
        agents=[error_handler_agent, final_assembler_agent, code_writer_agent],
        tasks=[error_check_task, integration_task, code_gen_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    if not result or not result.tasks_output or len(result.tasks_output) != 3:
        return "Error: Final assembly workflow did not produce the expected number of task outputs."

    error_check_output_obj = result.tasks_output[0]
    integration_output_obj = result.tasks_output[1]
    code_gen_output_obj = result.tasks_output[2]

    # Simplified check: if .raw is missing or empty, it's a failure post-retries.
    # A more robust check would use a specific status field from crewAI if available.
    error_check_raw = getattr(error_check_output_obj, 'raw', None)
    integration_raw = getattr(integration_output_obj, 'raw', None)
    code_gen_raw = getattr(code_gen_output_obj, 'raw', None)

    if not error_check_raw: # Check for empty string as well, as .raw might exist but be empty.
        return f"Error: Error check task failed in final_assembly_workflow. No output or empty output."
    if not integration_raw:
        return f"Error: Integration task failed in final_assembly_workflow. No output or empty output. Error check output: {error_check_raw}"
    if not code_gen_raw:
        return f"Error: Code generation task failed in final_assembly_workflow. No output or empty output. Integration plan: {integration_raw}"

    # If all tasks seem to have produced raw output
    final_code_output = code_gen_raw
    # Potentially add a check here if final_code_output itself is an error message passed through the guardrail
    # This is a simple heuristic: if the output is short and contains "error", it might be an error message.
    if ("error" in final_code_output.lower() or "failed" in final_code_output.lower()) and len(final_code_output) < 250:
         return f"Error: Code generation task may have produced an error message: '{final_code_output}'. Integration plan: {integration_raw}"

    return final_code_output
