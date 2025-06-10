from crewai import Crew, Process, Agent, Task
from crewai.project import CrewBase, agent, crew, task

# Import actual dev utility agents
from crewai.qrew.agents.dev_utilities import (
    code_writer_agent,
    debugger_agent,
    tester_agent
)

@CrewBase
class CodeWritingCrew:
    """
    CodeWritingCrew focuses on code generation, debugging, and testing tasks,
    utilizing specialized agents from dev_utilities.
    """
    # tasks_config = 'config/code_writing_crew_tasks.yaml' # Example path

    @property
    def writer(self) -> Agent: # Renamed for brevity
        return code_writer_agent

    @property
    def debugger(self) -> Agent: # Renamed for brevity
        return debugger_agent

    @property
    def tester(self) -> Agent: # Renamed for brevity
        return tester_agent

    # Tasks defined by this crew, now assigned to actual agents
    @task
    def code_generation_task(self) -> Task:
        return Task(
            description="Generate code based on the following requirements: {code_requirements}. "
                        "Ensure the code is clean, follows coding standards, and includes necessary comments and basic error handling. "
                        "Input: {code_requirements}, {target_language_or_framework}.",
            expected_output="Well-written and functional code for {code_requirements} in {target_language_or_framework}, "
                            "including inline documentation and ready for initial review or testing.",
            agent=self.writer # type: ignore[attr-defined]
        )

    @task
    def debugging_task(self) -> Task:
        return Task(
            description="Debug the provided {code_to_debug_snippet_or_path} to resolve the reported {issue_description}. "
                        "Identify the root cause, implement a robust fix, and explain the changes. "
                        "Input: {code_to_debug_snippet_or_path}, {issue_description}, {steps_to_reproduce_bug}.",
            expected_output="Corrected code with the identified bug fixed. "
                            "A brief report detailing the root cause, the fix applied, and verification steps.",
            agent=self.debugger, # type: ignore[attr-defined]
            context=[self.code_generation_task] # Optional context: debugging might follow initial generation
        )

    @task
    def unit_testing_task(self) -> Task: # Made more specific to unit testing
        return Task(
            description="Write and execute unit tests for the {code_module_or_function} to ensure its correctness and reliability. "
                        "Achieve a target of {target_coverage_percentage}% code coverage if specified. "
                        "Input: {code_module_or_function_path}, {test_specifications_or_requirements}, {target_coverage_percentage}.",
            expected_output="A suite of unit tests for {code_module_or_function}. "
                            "A test execution report showing all tests passing and code coverage achieved. "
                            "Any identified bugs from testing should be reported.",
            agent=self.tester, # type: ignore[attr-defined]
            context=[self.debugging_task] # Testing usually follows debugging (or initial dev)
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Code Writing Utility crew"""
        return Crew(
            agents=[self.writer, self.debugger, self.tester],
            tasks=self.tasks,
            process=Process.sequential, # These tasks often follow a sequence
            verbose=True
        )

# Example usage (conceptual)
# if __name__ == "__main__":
#     inputs = {
#         'code_requirements': 'a Python class for managing a simple TO-DO list with add, remove, and view functionalities',
#         'target_language_or_framework': 'Python',
#         'code_to_debug_snippet_or_path': 'todo_list_v1.py', # Assume this file has the generated code or existing buggy code
#         'issue_description': 'Removing an item from an empty list causes a crash.',
#         'steps_to_reproduce_bug': '1. Create an empty TodoList. 2. Call remove_item("any_item").',
#         'code_module_or_function_path': 'todo_list_v2.py', # Assume this is the debugged version
#         'test_specifications_or_requirements': 'Test all public methods, including edge cases like empty list, item not found.',
#         'target_coverage_percentage': '90'
#     }
#     code_writing_crew_instance = CodeWritingCrew()
#     result = code_writing_crew_instance.crew().kickoff(inputs=inputs)
#     print("\n\nCode Writing Crew execution finished.")
#     print("Result:")
#     print(result)
