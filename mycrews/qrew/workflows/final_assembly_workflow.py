from crewai import Crew, Process, Task
from ..orchestrators.final_assembler_agent.agent import final_assembler_agent
from ..agents.dev_utilities import code_writer_agent
from ..agents.dev_utilities import debugger_agent as error_handler_agent

def run_final_assembly_workflow(inputs: dict):
    # Error checking phase
    error_check_task = Task(
        description="Verify all components for integration readiness",
        agent=error_handler_agent,
        expected_output="Error report and readiness assessment",
        context=inputs["components"]
    )

    # Integration planning
    integration_task = Task(
        description="Create integration plan based on components",
        agent=final_assembler_agent,
        expected_output="Detailed integration plan",
        context=[inputs["architecture"], inputs["components"]]
    )

    # Code generation
    code_gen_task = Task(
        description="Generate final integrated codebase",
        agent=code_writer_agent,
        expected_output="Complete, runnable codebase",
        context=[inputs["architecture"], inputs["components"]]
    )

    # Execute final assembly
    crew = Crew(
        agents=[error_handler_agent, final_assembler_agent, code_writer_agent],
        tasks=[error_check_task, integration_task, code_gen_task],
        process=Process.sequential,
        verbose=True
    )

    return crew.kickoff()
