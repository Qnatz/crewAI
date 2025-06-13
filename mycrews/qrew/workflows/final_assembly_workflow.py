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
        expected_output="Error report and readiness assessment"
    )

    # Integration planning
    integration_task = Task(
        description=f"Create integration plan based on components. "                     f"The overall project architecture is: {architecture_summary_str}. "                     f"The components to integrate are: {components_summary_str}",
        agent=final_assembler_agent,
        expected_output="Detailed integration plan"
    )

    # Code generation
    code_gen_task = Task(
        description=f"Generate final integrated codebase. "                     f"The overall project architecture is: {architecture_summary_str}. "                     f"The components to use for generation are: {components_summary_str}",
        agent=code_writer_agent,
        expected_output="Complete, runnable codebase"
    )

    # Execute final assembly
    crew = Crew(
        agents=[error_handler_agent, final_assembler_agent, code_writer_agent],
        tasks=[error_check_task, integration_task, code_gen_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    # The tasks are error_check_task, integration_task, code_gen_task in sequence.
    # The final output is from code_gen_task, which would be the last one.
    if result and result.tasks_output and len(result.tasks_output) == 3:
        # Assuming code_gen_task is the third task and its output is what we want.
        final_code_output = result.tasks_output[2].raw_output
        return final_code_output
    elif result and result.tasks_output: # Fallback if unexpected number of task outputs
        return result.tasks_output[-1].raw_output # Return output of the very last task
    else:
        return "Error: Final assembly workflow did not produce a recognizable output."
