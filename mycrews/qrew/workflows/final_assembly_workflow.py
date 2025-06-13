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

    return crew.kickoff()
