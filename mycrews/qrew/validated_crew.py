from typing import Optional, Any, List
import logging

from crewai import Crew, Agent, Task
# from crewai.enums import TaskProcess # Removed
# from crewai.shared import SharedContext # Removed
# from crewai.utilities.task_output_adapter import TaskOutputAdapter # Removed

# from crewai.utilities.logger import logger as crewai_logger # Using standard logging for this example

# Configure a logger for this module
log = logging.getLogger(__name__)
# Example: If you want to see these logs, configure basicConfig once in your main entry point
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


class QualityGateFailedError(Exception):
    """Custom exception for when a task fails the quality gate after all retries."""
    def __init__(self, task_description: str, messages: List[str]):
        self.task_description = task_description
        self.messages = messages
        super().__init__(f"Task '{task_description}' failed quality gate after all retries. Issues: {'; '.join(messages)}")


class ValidatedCrew(Crew):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._keyword_check_enabled: bool = True
        self._custom_validators: List[callable] = []

        # Check Task.DEFAULT_SCHEMA for payload configuration compatibility
        if "payload" not in Task.DEFAULT_SCHEMA or not isinstance(Task.DEFAULT_SCHEMA["payload"], dict): # type: ignore
            log.warning("Task.DEFAULT_SCHEMA does not define 'payload' as a dictionary. "
                        "'previousFeedback' injection might not work as expected.")
        elif Task.DEFAULT_SCHEMA["payload"].get("default", "NOT_SET") == "NOT_SET": # type: ignore
            log.warning("Task.DEFAULT_SCHEMA['payload'] does not have a 'default' key. "
                        "Consider adding 'default: {}' for robust 'previousFeedback' injection.")


    def configure_quality_gate(
        self,
        keyword_check: bool = True,
        custom_validators: Optional[List[callable]] = None
    ):
        """Configures the quality gate settings for this crew."""
        self._keyword_check_enabled = keyword_check
        self._custom_validators = custom_validators if custom_validators is not None else []
        log.info(
            f"ValidatedCrew quality gate configured for crew (verbose={self.verbose}): " # Accessing self.verbose
            f"Keyword Check={'Enabled' if self._keyword_check_enabled else 'Disabled'}, "
            f"Custom Validators={[v.__name__ for v in self._custom_validators] if self._custom_validators else 'None'}"
        )

    def delegate_task(self, task: Task, agent: Optional[Agent] = None, context: Optional[str] = None) -> Any:
        """
        Delegates a task to an agent, applying quality gate checks and retries.
        """
        if not isinstance(task, Task):
            # Using type(task).__name__ for more informative error
            raise ValueError(f"ValidatedCrew.delegate_task expects a Task object, got {type(task).__name__}.")

        target_agent = agent if agent else task.agent
        if not target_agent:
            raise ValueError(f"No agent specified for task: {task.description}. "
                             "Either pass an agent parameter or ensure task.agent is set.")
        if not isinstance(target_agent, Agent):
            raise ValueError(f"Invalid agent provided for task '{task.description}'. Expected Agent instance, got {type(target_agent).__name__}.")

        # Get maxRetries from task or Task.DEFAULT_SCHEMA, ensuring it's an int >= 0
        max_retries_from_task = getattr(task, 'maxRetries', None)
        if isinstance(max_retries_from_task, int) and max_retries_from_task >= 0:
            max_retries = max_retries_from_task
        else:
            schema_max_retries = Task.DEFAULT_SCHEMA.get('maxRetries', {}).get('default', 1) # type: ignore
            if isinstance(schema_max_retries, int) and schema_max_retries >= 0:
                max_retries = schema_max_retries
            else:
                log.warning(f"Invalid maxRetries value in Task.DEFAULT_SCHEMA: {schema_max_retries}. Defaulting to 1.")
                max_retries = 1

        if max_retries_from_task is not None and max_retries_from_task != max_retries:
            log.info(f"Task '{task.description}' maxRetries ({max_retries_from_task}) is overridden by schema default or invalid. Using: {max_retries}.")


        for attempt in range(max_retries + 1):
            log.info(f"Executing task '{task.description}' with agent '{target_agent.role}'. Attempt {attempt + 1}/{max_retries + 1}.")

            if task.payload is None: # Ensure payload exists
                task.payload = {}

            try:
                result = target_agent.execute_task(task=task, context=context)
            except Exception as e:
                log.error(f"Exception during task execution by '{target_agent.role}' for task '{task.description}' on attempt {attempt + 1}: {e}", exc_info=True)
                if attempt < max_retries:
                    task.payload["previousFeedback"] = f"Execution error on attempt {attempt + 1}: {str(e)}"
                    log.info(f"Retrying task '{task.description}' due to execution error.")
                    continue
                else:
                    raise QualityGateFailedError(task.description, [f"Execution error on final attempt: {str(e)}"]) from e

            passed_quality_gate = True
            feedback_messages: List[str] = []

            if self._keyword_check_enabled and task.successCriteria:
                result_str_for_keyword_check = str(result.get("output", result) if isinstance(result, dict) else result)
                if not result_str_for_keyword_check and not task.successCriteria: # Allow empty output if no criteria
                    pass # Considered a pass
                elif not result_str_for_keyword_check and task.successCriteria:
                     passed_quality_gate = False
                     feedback_messages.append("Output was empty, but successCriteria were expected.")
                     log.info(f"Task '{task.description}' failed keyword check: Output empty, criteria present.")
                else:
                    for criterion in task.successCriteria:
                        if criterion.lower() not in result_str_for_keyword_check.lower():
                            passed_quality_gate = False
                            feedback_messages.append(f"Keyword criterion not met: '{criterion}'")
                            log.info(f"Task '{task.description}' failed keyword check: '{criterion}' not in output.")

            if self._custom_validators:
                for validator in self._custom_validators:
                    try:
                        if not validator(task, result):
                            passed_quality_gate = False
                            # Assuming validator logs its own failure reason if it wants to be specific
                            feedback_messages.append(f"Custom validator '{validator.__name__}' failed.")
                            log.info(f"Task '{task.description}' failed custom validator '{validator.__name__}'.")
                    except Exception as e:
                        passed_quality_gate = False
                        feedback_messages.append(f"Error in custom validator '{validator.__name__}': {str(e)}")
                        log.error(f"Task '{task.description}': Error executing custom validator '{validator.__name__}': {e}", exc_info=True)

            if passed_quality_gate:
                log.info(f"Task '{task.description}' passed quality gate on attempt {attempt + 1}.")
                if "previousFeedback" in task.payload:
                    del task.payload["previousFeedback"]
                return result

            if attempt < max_retries:
                task.payload["previousFeedback"] = ". ".join(feedback_messages)
                log.info(f"Task '{task.description}' failed quality gate. Feedback: '{task.payload['previousFeedback']}'. Retrying ({attempt + 1}/{max_retries} retries used)...")
            else:
                log.error(f"Task '{task.description}' failed quality gate after {max_retries + 1} attempts. Final issues: {'; '.join(feedback_messages)}")
                raise QualityGateFailedError(task.description, feedback_messages)

        # Fallback, should ideally not be reached if logic is correct
        final_feedback = feedback_messages if 'feedback_messages' in locals() and feedback_messages else ["Unknown state after retries."]
        raise QualityGateFailedError(task.description, final_feedback)

    def kickoff(self, inputs: Optional[dict] = None) -> Any:
        """
        Kicks off the crew's tasks, ensuring each task goes through the
        quality gate defined in `delegate_task`.
        This override is for sequential processing.
        """
        log.info(f"ValidatedCrew kickoff initiated. Inputs: {inputs if inputs else 'None'}")

        if str(self.process).lower() == "sequential": # Changed condition
            if not self.tasks:
                log.warning("ValidatedCrew kickoff: No tasks to execute.")
                return "No tasks to execute."

            task_outputs = [] # Store all task outputs

            for task in self.tasks:
                if not task.agent:
                    # Try to assign a default agent from the crew if available and task has no agent
                    if len(self.agents) == 1: # Or some other logic to pick a default
                        task.agent = self.agents[0]
                        log.info(f"Task '{task.description}' has no agent. Assigned default agent '{task.agent.role}'.")
                    else:
                        raise ValueError(
                            f"Task '{task.description}' has no agent assigned and no single default agent could be determined for the crew."
                        )

                original_description = task.description # Store before potential interpolation
                if inputs:
                    try:
                        # Ensure description is a string before calling format
                        if isinstance(task.description, str):
                            task.description = task.description.format(**inputs)
                            log.info(f"Interpolated task '{original_description}' to '{task.description}' using kickoff inputs.")
                        else:
                            log.warning(f"Task '{original_description}' description is not a string. Skipping input interpolation.")
                    except KeyError as e:
                        log.warning(f"KeyError during input interpolation for task '{original_description}': {e}. Using original description.")
                        task.description = original_description # Revert if interpolation fails

                log.info(f"Executing task via delegate_task (from kickoff): {task.description}")
                # Use task.agent as it's now guaranteed to be set or error was raised
                task_result = self.delegate_task(task=task, agent=task.agent)

                log.info(f"Task '{task.description}' completed via kickoff. Result: {str(task_result)[:200]}...")
                task_outputs.append(task_result)

                # Restore original task description
                task.description = original_description


            # Return the output of the last task, similar to standard sequential kickoff
            return task_outputs[-1] if task_outputs else "No task outputs from kickoff."

        elif str(self.process).lower() == "hierarchical": # Changed condition
            if not self.manager_agent:
                raise ValueError("Manager agent not set for hierarchical process.")
            log.info(f"ValidatedCrew kickoff: Hierarchical process with manager agent '{self.manager_agent.role}'.")

            manager_task_description = "Coordinate and manage the defined tasks to achieve the crew's overall goal."
            if inputs: # Try to interpolate inputs into manager task description if they seem relevant
                try:
                    # A generic way to make inputs available, manager agent needs to know how to use them
                    manager_task_description = f"{manager_task_description} Initial inputs for the overall goal: {inputs}"
                except Exception: # Broad catch if inputs are not string-formattable easily
                    pass


            manager_task = Task(
                description=manager_task_description,
                agent=self.manager_agent,
                expected_output="The final result from the coordinated execution of all tasks."
            )
            # If the manager agent needs to know about the sub-tasks, they should be passed in the payload
            # or the manager agent's logic should be aware of `self.tasks` from the crew.
            # For now, we keep it simple; manager is expected to have its logic for task discovery or gets them via tools.
            return self.delegate_task(task=manager_task, agent=self.manager_agent)
        else:
            raise NotImplementedError(
                f"Process '{self.process}' not implemented in ValidatedCrew.kickoff."
            )
