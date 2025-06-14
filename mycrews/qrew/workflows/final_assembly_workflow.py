import json
from crewai import Crew, Process, Task
from ..orchestrators.final_assembler_agent.agent import final_assembler_agent
from ..agents.dev_utilities import code_writer_agent
from ..agents.dev_utilities import debugger_agent as error_handler_agent

def run_final_assembly_workflow(inputs: dict):
    components_summary_str = json.dumps(inputs.get("components", {}), indent=2)
    architecture_summary_str = json.dumps(inputs.get("architecture", {}), indent=2)

    # Error checking phase
    error_check_task = Task(
        description=f"Verify all components for integration readiness. "                     f"The components to verify are: {components_summary_str}",
        agent=error_handler_agent,
        expected_output="Error report and readiness assessment",
        max_retries=1,
        guardrail="Ensure the output is a comprehensive error report and readiness assessment. It should list potential issues and state if components are ready for integration."
    )

    # Integration planning
    integration_task = Task(
        description=f"Create integration plan based on components. "                     f"The overall project architecture is: {architecture_summary_str}. "                     f"The components to integrate are: {components_summary_str}",
        agent=final_assembler_agent,
        expected_output="Detailed integration plan",
        max_retries=1,
        guardrail="Ensure the output is a detailed integration plan, outlining steps and considerations for combining all provided software components."
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
