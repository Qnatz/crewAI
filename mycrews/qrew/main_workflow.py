import json # Added for parsing sub-task definitions
import logging # Added for logging in dynamic task creation
from typing import Any, Optional # Added Optional
from crewai import Process, Task # Crew removed from here
from crewai.utilities.i18n import I18N
import os
from .llm_config import default_llm # Added for qrew_main_crew
from .config import example_summary_validator # Imported validator
from .validated_crew import ValidatedCrew # Added ValidatedCrew import
# from crewai import Task # Added for the validator's type hint - already imported

log = logging.getLogger(__name__) # Define module-level logger

# Orchestrator Agents
from .orchestrators.idea_interpreter_agent.agent import idea_interpreter_agent
from .orchestrators.tech_vetting_council_agent.agent import tech_vetting_council_agent
from .orchestrators.project_architect_agent.agent import project_architect_agent

# Tech Stack Committee Agents
from .orchestrators.tech_stack_committee.constraint_checker_agent.agent import constraint_checker_agent
from .orchestrators.tech_stack_committee.stack_advisor_agent.agent import stack_advisor_agent
from .orchestrators.tech_stack_committee.documentation_writer_agent.agent import documentation_writer_agent

from .taskmaster import taskmaster_agent # Added taskmaster_agent import

# Custom Tools
from .tools.custom_agent_tools import CustomDelegateWorkTool, CustomAskQuestionTool

# Instantiate custom tools at module level
custom_delegate_tool = CustomDelegateWorkTool()
custom_ask_tool = CustomAskQuestionTool()

# --- Main Qrew Crew Setup ---
# example_summary_validator is now imported from config.py

all_qrew_agents = [
    idea_interpreter_agent,
    tech_vetting_council_agent,
    project_architect_agent,
    constraint_checker_agent,
    stack_advisor_agent,
    documentation_writer_agent,
    taskmaster_agent  # Add taskmaster_agent here
]

qrew_main_crew = ValidatedCrew( # Changed from Crew to ValidatedCrew
    agents=all_qrew_agents, # Use the comprehensive list
    tasks=[],              # Tasks can remain empty at initialization
    llm=default_llm,
    verbose=True,
)

print("Configuring Quality Gate for qrew_main_crew...")
qrew_main_crew.configure_quality_gate(
    keyword_check=True,
    custom_validators=[example_summary_validator]
)
print("qrew_main_crew initialized and Quality Gate configured in main_workflow.py.")
# --- End of Main Qrew Crew Setup ---

# Helper function for robust output string extraction
def get_task_output_string(task_output_obj: Any, task_desc_for_log: str) -> Optional[str]:
    """
    Attempts to extract a raw string output from a Task's output object.
    Tries attributes 'raw', then 'raw_output'. If object is str, returns it.
    Falls back to str(object). Logs the method used. Returns None if output is effectively empty.
    """
    if hasattr(task_output_obj, 'raw') and isinstance(task_output_obj.raw, str) and task_output_obj.raw.strip():
        log.info(f"Extracted output for '{task_desc_for_log}' using .raw attribute.")
        return task_output_obj.raw.strip()
    elif hasattr(task_output_obj, 'raw_output') and isinstance(task_output_obj.raw_output, str) and task_output_obj.raw_output.strip():
        log.info(f"Extracted output for '{task_desc_for_log}' using .raw_output attribute.")
        return task_output_obj.raw_output.strip()
    elif isinstance(task_output_obj, str) and task_output_obj.strip():
        log.info(f"Task output for '{task_desc_for_log}' is already a string.")
        return task_output_obj.strip()
    else:
        str_output = str(task_output_obj).strip()
        log.warning(f"Could not find .raw or .raw_output string attributes for '{task_desc_for_log}', "
                    f"nor was the object itself a non-empty string. Falling back to str(). Type was: {type(task_output_obj)}, Str_output: '{str_output[:100]}...'")
        if str_output and str_output.lower() != "none": # Check if stringified output is meaningful
            return str_output
        log.warning(f"Fallback str(task_output_obj) for '{task_desc_for_log}' resulted in 'None' or empty string.")
        return None

def run_idea_to_architecture_workflow(workflow_inputs: dict):
    print("## Initializing Idea to Architecture Workflow Agents & Tasks...")

    # Remove CustomDelegateWorkTool and CustomAskQuestionTool from tech_vetting_council_agent
    if hasattr(tech_vetting_council_agent, 'tools') and tech_vetting_council_agent.tools is not None:
        tech_vetting_council_agent.tools = [
            tool for tool in tech_vetting_council_agent.tools
            if not isinstance(tool, (CustomDelegateWorkTool, CustomAskQuestionTool))
        ]
    else:
        tech_vetting_council_agent.tools = []

    all_agents_for_crew = [
        idea_interpreter_agent,
        tech_vetting_council_agent,
        project_architect_agent,
        constraint_checker_agent,
        stack_advisor_agent,
        documentation_writer_agent
    ]

    default_i18n_instance = I18N()
    for agent_instance in all_agents_for_crew:
        if not hasattr(agent_instance, 'i18n') or agent_instance.i18n is None:
            agent_instance.i18n = default_i18n_instance
        if not hasattr(agent_instance, 'llm') or agent_instance.llm is None:
            print(f"Warning: Agent {agent_instance.role} in run_idea_to_architecture_workflow appears to be missing an LLM configuration.")

    # Task Definitions
    task_interpret_idea = Task(
        description='''Analyze the provided user idea: "{user_idea}", stakeholder feedback: "{stakeholder_feedback}", and market research data: "{market_research_data}".
Your primary goal is to deeply understand these inputs.
Consult the Knowledge Base for any relevant past projects, architectural decisions, or definitions that could clarify or enrich the user\'s concept.
Produce a structured set of technical requirements and a detailed feature breakdown.
Ensure the technical requirements are clear, testable, and complete.
The feature breakdown should detail individual components and user interactions for key features described in the user idea.''',
        expected_output='''A comprehensive technical requirements specification document AND a detailed feature breakdown document.
The technical requirements should include:
- Detailed user stories with acceptance criteria.
- Functional requirements.
- Non-functional requirements.
- Data requirements.
- A glossary of terms.
- Identified ambiguities.
The feature breakdown should detail individual components and user interactions for key features.''',
        agent=idea_interpreter_agent,
        successCriteria=[
            "technical requirements specification created",
            "feature breakdown document created",
            "user stories with acceptance criteria included",
            "functional requirements listed",
            "non-functional requirements listed",
            "data requirements identified",
            "glossary of terms provided"
        ]
    )

    task_vet_requirements_planning = Task(
        description='''Your primary goal is to plan the vetting process for the Technical Requirements Specification and Feature Breakdown (available from 'task_interpret_idea' in your context).
You MUST define the sub-tasks to be delegated to 'ConstraintCheckerAgent' and 'StackAdvisorAgent'.
For 'ConstraintCheckerAgent', the sub-task should be to "Review the provided 'proposed_solution' (Technical Requirements Specification and Feature Breakdown) against the 'project_constraints_document' (value: "{constraints}"). Identify any violations or potential conflicts regarding budget, team skills, security policies, licensing, or infrastructure."
For 'StackAdvisorAgent', the sub-task should be to "Analyze the provided 'project_requirements' (Technical Requirements Specification and Feature Breakdown) to propose an optimal technology stack. Consider 'team_skills' and 'budget_constraints' (both from "{constraints}") and 'existing_architecture_details' (value: "None - new project"). Provide justifications for stack choices, considering scalability, maintainability, and alignment with the technical vision."

IMPORTANT: Your entire response MUST be ONLY a single, valid JSON object.
Do not include any explanatory text, greetings, or any characters before or after the JSON object.
Ensure all string values within the JSON are properly quoted.
There should be no extraneous characters or words outside of the defined JSON structure itself.

The JSON object must have a key "sub_tasks_to_delegate". The value should be a list of dictionaries.
Each dictionary in the list represents a sub-task and must include:
- "task_description_template": (string) A string that is the description for the sub-agent, using placeholders like {{PLACEHOLDER_NAME}} for data that needs to be injected from the main workflow context.
- "required_context_keys": (list of strings) A list of strings, where each string is a placeholder name used in the task_description_template (e.g., ["PLACEHOLDER_NAME_1", "PLACEHOLDER_NAME_2"]). These keys MUST correspond to data available in the broader workflow context, such as the output of 'task_interpret_idea' or initial '{{constraints}}'.
- "assigned_agent_role": (string) The role of the agent to delegate to (e.g., "ConstraintCheckerAgent", "StackAdvisorAgent").
- "successCriteria": (list of strings) Specific criteria for the sub-task's success (e.g., ["violations identified", "compliance report generated"]).

Example sub-task definition:
{
  "task_description_template": "Review the proposed solution (details: {{SOLUTION_DETAILS}}) against the project constraints (document: {{CONSTRAINTS_DOC}}). Identify violations.",
  "required_context_keys": ["SOLUTION_DETAILS", "CONSTRAINTS_DOC"],
  "assigned_agent_role": "ConstraintCheckerAgent",
  "successCriteria": ["Violations identified", "Report generated"]
}
Your response must be exactly in this format, with a top-level key "sub_tasks_to_delegate" containing a list of such dictionaries.
''',
        expected_output='''A single, valid JSON object with a key "sub_tasks_to_delegate". The value must be a list of dictionaries, where each dictionary contains "task_description_template" (string), "required_context_keys" (list of strings), "assigned_agent_role" (string), and "successCriteria" (list of strings). No other text or characters outside this JSON object.''',
        agent=tech_vetting_council_agent,
        context=[task_interpret_idea],
        successCriteria=[
            "sub_tasks_to_delegate list provided",
            "ConstraintCheckerAgent sub-task defined",
            "StackAdvisorAgent sub-task defined",
            "payloads for sub-tasks correctly structured",
            "successCriteria for sub-tasks defined"
        ]
    )

    # This is the new task_design_architecture_planning, replacing the old task_design_architecture
    task_design_architecture_planning = Task(
        description='''Your primary goal is to PLAN the detailed design of a software architecture.
Based on:
1. Original Technical Requirements & Feature Breakdown (available as {user_idea_details_str}).
2. The Vetting Report & Final Technical Guidelines (available as {vetting_report_and_guidelines_str}).
3. Overall project constraints (available as {original_constraints_str}).
4. Project's technical vision (available as {technical_vision_str}).

You must define the sub-tasks to be delegated for designing various architectural components (e.g., database schema, API design for specific modules, UI component structure).
Return a JSON object with a key "sub_tasks_to_delegate". The value should be a list of dictionaries.
IMPORTANT: Your entire response MUST be ONLY this single, valid JSON object.
Do not include any explanatory text, greetings, or any characters before or after the JSON object.
Ensure all string values within the JSON are properly quoted.
There should be no extraneous characters or words outside of the defined JSON structure itself.

The JSON structure for each sub-task dictionary in the list is:
- "task_description_template": (string) A string that is the description for the sub-agent, using placeholders like {{PLACEHOLDER_NAME}} for data that needs to be injected from the main workflow context.
- "required_context_keys": (list of strings) A list of strings, where each string is a placeholder name used in the task_description_template (e.g., ["PLACEHOLDER_NAME_1"]). These keys MUST correspond to data available in the broader workflow context (e.g., output of 'task_interpret_idea' as 'USER_IDEA_DETAILS', output of vetting synthesis as 'VETTING_REPORT', original constraints as 'PROJECT_CONSTRAINTS').
- "assigned_agent_role": (string) The role of the agent to delegate to.
- "successCriteria": (list of strings) Specific criteria for the sub-task's success.

Example sub-task definition:
{
Example sub-task definition:
{
  "task_description_template": "Design the database schema based on these requirements: {{USER_IDEA_DETAILS}} and adhering to guidelines: {{VETTING_REPORT}}. Focus on PostgreSQL.",
  "required_context_keys": ["USER_IDEA_DETAILS", "VETTING_REPORT"],
  "assigned_agent_role": "DatabaseAdminAgent",
  "successCriteria": ["Schema diagram created", "SQL DDL scripts provided"]
}

Example of the overall JSON structure:
{
  "sub_tasks_to_delegate": [
    {
      "task_description_template": "Design component X based on these requirements: {{COMPONENT_X_REQUIREMENTS}}",
      "required_context_keys": ["COMPONENT_X_REQUIREMENTS"],
      "assigned_agent_role": "SpecialistRoleA",
      "successCriteria": ["Design complete", "Docs provided"]
    }
  ]
}
Your response must be exactly in this format.
''',
        expected_output='''A single, valid JSON object with a key "sub_tasks_to_delegate". The value must be a list of dictionaries, where each dictionary contains "task_description_template" (string), "required_context_keys" (list of strings), "assigned_agent_role" (string), and "successCriteria" (list of strings). No other text or characters outside this JSON object.''',
        agent=project_architect_agent, # Assigned to Project Architect
        # Context will be implicitly handled by the formatted description during execution
        successCriteria=[
            "component design sub-tasks defined",
            "delegation plan for architecture created",
            "payloads for component tasks structured",
            "successCriteria for component tasks specified"
        ],
        # Payload will be added dynamically during execution, so not defined here.
    )

    # The old task_design_architecture Task object is now replaced by task_design_architecture_planning.
    # The actual synthesis of the architecture will be a new task: task_design_architecture_synthesis.

    idea_to_architecture_crew = ValidatedCrew( # Changed from Crew to ValidatedCrew
        agents=all_agents_for_crew,
        tasks=[task_interpret_idea, task_vet_requirements_planning], # task_design_architecture_planning is NOT part of this initial crew
        process=Process.sequential,
        verbose=True
    )

    print(f"Kicking off Idea-to-Architecture workflow (Phase 1: Planning) with inputs: {workflow_inputs}")

    agent_role_map = {
        "ConstraintCheckerAgent": constraint_checker_agent,
        "StackAdvisorAgent": stack_advisor_agent,
        "ProjectArchitectAgent": project_architect_agent, # Added for potential self-delegation or generic assignment
        # Add other specific roles if new specialist agents are created and imported
        # "BackendDeveloperAgent": backend_dev_agent,
        # "FrontendDeveloperAgent": frontend_dev_agent,
    }

    # Initial crew for idea interpretation and vetting planning
    planning_crew_result_obj = idea_to_architecture_crew.kickoff(inputs=workflow_inputs)

    output_of_task_interpret_idea_str = "Error: Could not retrieve task_interpret_idea output" # Default
    if planning_crew_result_obj and hasattr(planning_crew_result_obj, 'tasks') and planning_crew_result_obj.tasks:
        interpret_idea_completed_task = None
        for completed_task in planning_crew_result_obj.tasks:
            if hasattr(completed_task, 'description') and isinstance(completed_task.description, str) and \
               task_interpret_idea.description in completed_task.description:
                interpret_idea_completed_task = completed_task
                break

        if interpret_idea_completed_task and hasattr(interpret_idea_completed_task, 'output'):
            extracted_str = get_task_output_string(interpret_idea_completed_task.output, "task_interpret_idea")
            if extracted_str:
                 output_of_task_interpret_idea_str = extracted_str
            else:
                 log.warning("get_task_output_string returned None or empty for task_interpret_idea.")
        elif interpret_idea_completed_task:
            log.warning("task_interpret_idea (completed) found but has no 'output' attribute.")
        else:
            log.warning("task_interpret_idea (completed) not found in kickoff results.")

    if output_of_task_interpret_idea_str == "Error: Could not retrieve task_interpret_idea output":
        log.warning("Failed to retrieve specific output for 'task_interpret_idea'. Using fallback or error string.")
        # Fallback to workflow_inputs if essential and not found, or handle error
        # output_of_task_interpret_idea_str = str(workflow_inputs.get("user_idea", "User idea from workflow_inputs as fallback"))

    sub_task_definitions_json_str = None # Initialize
    if planning_crew_result_obj and hasattr(planning_crew_result_obj, 'tasks') and len(planning_crew_result_obj.tasks) > 0:
        vetting_planning_completed_task = None
        for completed_task in planning_crew_result_obj.tasks:
            if hasattr(completed_task, 'description') and isinstance(completed_task.description, str) and \
               task_vet_requirements_planning.description in completed_task.description:
                vetting_planning_completed_task = completed_task
                break

        if vetting_planning_completed_task and hasattr(vetting_planning_completed_task, 'output'):
            extracted_str = get_task_output_string(vetting_planning_completed_task.output, "task_vet_requirements_planning")
            if extracted_str:
                sub_task_definitions_json_str = extracted_str
            else:
                log.warning("get_task_output_string returned None or empty for task_vet_requirements_planning.")
        elif vetting_planning_completed_task:
            log.warning("task_vet_requirements_planning (completed) found but has no 'output' attribute.")
        else:
            log.warning("task_vet_requirements_planning (completed) not found in kickoff results by description match.")

    if not sub_task_definitions_json_str: # Check if still None or empty from tasks list processing
        # Fallback to direct .raw from kickoff result if that's a possible structure
        if hasattr(planning_crew_result_obj, 'raw') and isinstance(planning_crew_result_obj.raw, str) and planning_crew_result_obj.raw.strip():
            log.info("Using planning_crew_result_obj.raw for task_vet_requirements_planning output as tasks list processing failed or yielded empty.")
            sub_task_definitions_json_str = planning_crew_result_obj.raw.strip()
        # Fallback if kickoff result itself is a string
        elif isinstance(planning_crew_result_obj, str) and planning_crew_result_obj.strip():
             log.info("Using planning_crew_result_obj (string) for task_vet_requirements_planning output.")
             sub_task_definitions_json_str = planning_crew_result_obj.strip()

    if not sub_task_definitions_json_str:
        print("Error: Vetting Requirements Planning task did not produce a usable output string.")
        log.error("sub_task_definitions_json_str is None or empty after attempting all extraction methods.")
        return None

    print("\nProcessing output of Vetting Requirements Planning...")
    delegated_task_results = {}
    try:
        json_start_index = sub_task_definitions_json_str.find('{')
        json_end_index = sub_task_definitions_json_str.rfind('}') + 1
        actual_json_str = ""
        if json_start_index != -1 and json_end_index != -1:
            actual_json_str = sub_task_definitions_json_str[json_start_index:json_end_index]
            sub_task_data = json.loads(actual_json_str)
        else:
            raise json.JSONDecodeError("No JSON object found in Vetting Planning output", sub_task_definitions_json_str, 0)

        if "sub_tasks_to_delegate" not in sub_task_data:
            print("Error: 'sub_tasks_to_delegate' key missing in Vetting Planning output JSON.")
            print(f"Received JSON: {actual_json_str}")
            return None

        for sub_task_def in sub_task_data["sub_tasks_to_delegate"]:
            task_template = sub_task_def.get("task_description_template")
            context_keys = sub_task_def.get("required_context_keys", [])
            assigned_role = sub_task_def.get("assigned_agent_role")

            if not task_template or not assigned_role:
                log.warning(f"Skipping sub-task due to missing template or role: {sub_task_def}")
                continue

            actual_agent = agent_role_map.get(assigned_role)
            if not actual_agent:
                log.warning(f"Agent for role '{assigned_role}' not found. Skipping sub-task: {task_template[:70]}...")
                continue

            format_data = {}
            for key in context_keys:
                if key == "OUTPUT_OF_TASK_INTERPRET_IDEA": # Standardized key example
                    format_data[key] = output_of_task_interpret_idea_str
                elif key == "PROJECT_CONSTRAINTS": # Standardized key example
                    format_data[key] = workflow_inputs.get("constraints", f"[{key} - UNDEFINED IN WORKFLOW_INPUTS]")
                # Add more standardized keys here as you define them in prompts
                else:
                    log.warning(f"Context key '{key}' for vetting sub-task has no defined mapping. Using placeholder.")
                    format_data[key] = f"[{key} - MAPPING UNDEFINED]"

            try:
                final_description = task_template.format(**format_data)
            except KeyError as e:
                log.error(f"KeyError formatting description for vetting sub-task '{task_template[:70]}...': {e}. Data: {format_data}")
                final_description = task_template # Use template as fallback

            new_sub_task = Task(
                description=final_description,
                expected_output=sub_task_def.get("expected_output", "Actionable result for the delegated sub-task."),
                agent=actual_agent,
                successCriteria=sub_task_def.get("successCriteria", ["output generated"]),
            )

            log.info(f"Delegating vetting sub-task to {actual_agent.role}: {final_description[:70]}...")
            sub_task_result = qrew_main_crew.delegate_task(task=new_sub_task)
            delegated_task_results[assigned_role] = str(sub_task_result.raw if hasattr(sub_task_result, 'raw') else sub_task_result) # Store raw string output
            print(f"    Sub-task for {assigned_role} completed. Result: {str(sub_task_result)[:100]}...")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Vetting Requirements Planning output: {e}")
        print(f"Received output for parsing: '{actual_json_str}'")
        print(f"Original output from LLM: '{sub_task_definitions_json_str}'")
        return None
    except Exception as e:
        print(f"An error occurred during sub-task delegation: {e}")
        import traceback
        traceback.print_exc()
        return None

    print("\nPreparing Vetting Requirements Synthesis task...")
    synthesis_payload = {
        "constraint_checker_report": delegated_task_results.get("ConstraintCheckerAgent", "Not available"),
        "stack_advisor_report": delegated_task_results.get("StackAdvisorAgent", "Not available"),
        "original_user_idea": workflow_inputs.get("user_idea", "User idea not explicitly passed to synthesis payload."), # Or retrieve from task_interpret_idea.output
        "original_constraints": workflow_inputs.get("constraints", "Constraints not explicitly passed to synthesis payload.") # Or retrieve from workflow_inputs
    }

    # Note: 'idea_task_output_str' is already fetched before this block.
    synthesis_payload["idea_interpretation_output"] = output_of_task_interpret_idea_str


    synthesis_desc_vetting = f"""Synthesize the findings from the Constraint Checker and Stack Advisor.
Constraint Checker Report: {synthesis_payload['constraint_checker_report']}
Stack Advisor Report: {synthesis_payload['stack_advisor_report']}
The original technical requirements and feature breakdown were based on: {synthesis_payload['idea_interpretation_output']}
Original project constraints were: {synthesis_payload['original_constraints']}
Original user idea was: {synthesis_payload['original_user_idea']}
Compile a final 'Vetting Report' and a set of 'Final Technical Guidelines'."""
    task_vet_requirements_synthesis = Task(
        description=synthesis_desc_vetting,
        expected_output='''A Vetting Report and a set of Final Technical Guidelines.
The Vetting Report should summarize: Stack Advisor's evaluation, Constraint Checker's compliance report, and the Tech Vetting Council's final decision/recommendations.
The Final Technical Guidelines should list approved technologies, patterns, or constraints.''',
        agent=tech_vetting_council_agent,
        # No 'input' parameter, data is in description
        successCriteria=[
            "Vetting Report compiled",
            "Final Technical Guidelines created",
            "Stack Advisor evaluation summarized",
            "Constraint Checker compliance report summarized",
            "Council recommendations included"
        ]
    )

    print("Executing Vetting Requirements Synthesis task using qrew_main_crew...")
    synthesis_result = qrew_main_crew.delegate_task(task=task_vet_requirements_synthesis)
    print(f"Synthesis task completed. Result: {str(synthesis_result)[:100]}...")

    # --- Architecture Design Phase ---
    print("\nPreparing Project Architecture Design Planning task...")

    # Determine the source for idea_interpretation_output for the architecture planning payload
    # 'output_of_task_interpret_idea_str' is already defined and populated.
    synthesis_result_vetting_str = str(synthesis_result.raw if hasattr(synthesis_result, 'raw') else synthesis_result)

    architecture_planning_context_data = {
        "USER_IDEA_DETAILS": output_of_task_interpret_idea_str,
        "VETTING_REPORT_AND_GUIDELINES": synthesis_result_vetting_str,
        "PROJECT_CONSTRAINTS": workflow_inputs.get("constraints", "Project constraints not provided."),
        "TECHNICAL_VISION": workflow_inputs.get("technical_vision", "Technical vision not provided.")
    }

    # The task_design_architecture_planning object is defined at the module level.
    # We format its description with runtime data to create an executable instance.
    original_planning_desc = task_design_architecture_planning.description

    try:
        # Format the description using only the keys expected by its template.
        # The LLM for task_design_architecture_planning itself defines what placeholders it uses (e.g., {user_idea_details_str})
        # For this execution, we pass a dict that the .format() method can use.
        # This requires that the original_planning_desc uses placeholders that match keys in architecture_planning_context_data,
        # OR that the LLM was instructed to use generic placeholders and we map them here.
        # Given the prompt asked for {user_idea_details_str} etc., we map them.
        execution_planning_desc = original_planning_desc.format(
            user_idea_details_str=architecture_planning_context_data["USER_IDEA_DETAILS"],
            vetting_report_and_guidelines_str=architecture_planning_context_data["VETTING_REPORT_AND_GUIDELINES"],
            original_constraints_str=architecture_planning_context_data["PROJECT_CONSTRAINTS"],
            technical_vision_str=architecture_planning_context_data["TECHNICAL_VISION"]
        )
    except KeyError as e:
        log.error(f"KeyError during description formatting for task_design_architecture_planning: {e}. Available data keys: {architecture_planning_context_data.keys()}")
        execution_planning_desc = original_planning_desc # Fallback

    executable_task_design_architecture_planning = Task(
        description=execution_planning_desc,
        expected_output=task_design_architecture_planning.expected_output,
        agent=project_architect_agent,
        successCriteria=task_design_architecture_planning.successCriteria
    )

    log.info("Executing Project Architecture Design Planning task using qrew_main_crew...")
    architecture_planning_result_obj = qrew_main_crew.delegate_task(
        task=executable_task_design_architecture_planning, # Use the new executable instance
    )
    architecture_planning_json_str = get_task_output_string(architecture_planning_result_obj, "executable_task_design_architecture_planning")
    if not architecture_planning_json_str: # Check if None or empty
        print("Error: Architecture Design Planning task did not produce a usable output string.") # Keep this error
        log.error("architecture_planning_json_str is None or empty after get_task_output_string for arch planning.")
        return None

    print("\nProcessing output of Architecture Design Planning...")
    architecture_delegated_task_results = {}
    try:
        json_start_index_arch = architecture_planning_json_str.find('{')
        json_end_index_arch = architecture_planning_json_str.rfind('}') + 1
        actual_arch_json_str = ""
        if json_start_index_arch != -1 and json_end_index_arch != -1:
            actual_arch_json_str = architecture_planning_json_str[json_start_index_arch:json_end_index_arch]
            architecture_sub_task_data = json.loads(actual_arch_json_str)
        else:
            raise json.JSONDecodeError("No JSON object found in Arch Design Planning output", architecture_planning_json_str, 0)

        if "sub_tasks_to_delegate" not in architecture_sub_task_data:
            print("Error: 'sub_tasks_to_delegate' key missing in architecture planning output JSON.")
            print(f"Received JSON: {actual_arch_json_str}")
            return None

        for sub_task_def in architecture_sub_task_data["sub_tasks_to_delegate"]:
            print(f"  Preparing architecture sub-task: {sub_task_def.get('task_description', 'No description')[:70]}...")
            assigned_role = sub_task_def.get("assigned_agent_role")
            # Use ProjectArchitectAgent as a fallback if a specific role is not in agent_role_map
            actual_agent = agent_role_map.get(assigned_role, project_architect_agent)
            if actual_agent == project_architect_agent and assigned_role not in agent_role_map:
                 log.warning(f"Agent for role '{assigned_role}' not found. Assigning to ProjectArchitectAgent for sub-task: {sub_task_def.get('task_description_template')[:70]}")

            arch_task_template = sub_task_def.get("task_description_template")
            arch_context_keys = sub_task_def.get("required_context_keys", [])

            if not arch_task_template:
                log.warning(f"Skipping architecture sub-task due to missing description template: {sub_task_def}")
                continue

            arch_format_data = {}
            for key in arch_context_keys:
                if key in architecture_planning_context_data:
                    arch_format_data[key] = architecture_planning_context_data[key]
                # Add more specific key mappings if the LLM uses different placeholders than the main context data keys
                elif key == "USER_IDEA_DETAILS": # Example if LLM used this specific key
                     arch_format_data[key] = output_of_task_interpret_idea_str
                elif key == "VETTING_REPORT":
                     arch_format_data[key] = synthesis_result_vetting_str
                else:
                    log.warning(f"Context key '{key}' for architecture sub-task has no defined mapping. Using placeholder.")
                    arch_format_data[key] = f"[{key} - MAPPING UNDEFINED]"

            try:
                final_arch_description = arch_task_template.format(**arch_format_data)
            except KeyError as e:
                log.error(f"KeyError formatting description for architecture sub-task '{arch_task_template[:70]}...': {e}. Data: {arch_format_data}")
                final_arch_description = arch_task_template # Fallback

            new_arch_sub_task = Task(
                description=final_arch_description,
                expected_output=sub_task_def.get("expected_output", "Detailed design for the architectural component."),
                agent=actual_agent,
                successCriteria=sub_task_def.get("successCriteria", ["component design completed"]),
            )

            print(f"    Delegating architecture sub-task to {actual_agent.role} ({actual_agent.id}) using qrew_main_crew...")
            arch_sub_task_result = qrew_main_crew.delegate_task(task=new_arch_sub_task)
            # Using description as key for uniqueness if multiple sub-tasks assigned to same role
            result_key = f"{assigned_role}_{sub_task_def.get('task_description', 'Unnamed_Arch_Sub_Task')[:30]}"
            architecture_delegated_task_results[result_key] = str(arch_sub_task_result.raw if hasattr(arch_sub_task_result, 'raw') else arch_sub_task_result)
            print(f"    Architecture sub-task for '{assigned_role}' completed.")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from Architecture Design Planning output: {e}")
        print(f"Received output for parsing: '{actual_arch_json_str}'")
        print(f"Original output from LLM: '{architecture_planning_json_str}'")
        return None
    except Exception as e:
        print(f"An error occurred during architecture sub-task delegation: {e}")
        import traceback
        traceback.print_exc()
        return None

    print("\nPreparing Architecture Design Synthesis task...")
    # architecture_synthesis_payload already defined using 'idea_output_for_arch_planning'
    # and 'synthesis_result_vetting_str' (implicitly via str(synthesis_result...))

    synthesis_desc_arch = f"""Synthesize all component design outputs into a final, detailed software architecture document.
Component Designs (JSON string): {json.dumps(architecture_delegated_task_results)}
Original Technical Requirements & Feature Breakdown: {architecture_planning_context_data["USER_IDEA_DETAILS"]}
Vetting Report & Final Technical Guidelines: {architecture_planning_context_data["VETTING_REPORT_AND_GUIDELINES"]}
Overall project constraints: {architecture_planning_context_data["PROJECT_CONSTRAINTS"]}
Project's technical vision: {architecture_planning_context_data["TECHNICAL_VISION"]}"""
    task_design_architecture_synthesis = Task(
        description=synthesis_desc_arch,
        expected_output='''A detailed software architecture document, including: High-level system diagrams, Technology stack recommendations for each component, Data model design overview, API design guidelines, Integration points, Non-functional requirements considerations.''',
        agent=project_architect_agent,
        # No 'input' parameter, data is in description
        successCriteria=[
            "software architecture document created",
            "high-level system diagrams included",
            "technology stack recommendations provided",
            "data model design overview included",
            "API design guidelines defined",
            "integration points identified"
        ]
    )

    print("Executing Architecture Design Synthesis task using qrew_main_crew...")
    architecture_synthesis_result = qrew_main_crew.delegate_task(
        task=task_design_architecture_synthesis,
    )
    print("Architecture Synthesis task completed.")

    print("\nIdea-to-Architecture (Full Workflow) complete.")
    return architecture_synthesis_result

if __name__ == "__main__":
# No change to this part of the file, it's just context. The main changes are above and inside run_idea_to_architecture_workflow.
    print("## Starting QREW Main Entry Point (which will call Idea to Architecture Workflow)")

    initial_user_idea_for_taskmaster = "Develop a market-leading application for interactive pet training that is fun and engaging. It should include video streaming, progress tracking, and social sharing features. We want it to be scalable and secure."
    simulated_taskmaster_output_as_user_idea = f"Project Brief from TaskMaster: The user wants an interactive pet training app. Key features: video, progress tracking, social sharing. Goal: fun, engaging, scalable, secure. Details: {initial_user_idea_for_taskmaster}"

    stakeholder_feedback_notes = "User retention is key. Gamification might be important. Mobile-first approach preferred."
    market_research_summary = "Competitors X and Y lack real-time interaction. Users want personalized training plans."
    project_constraints_for_workflow = "Team has strong Python and React skills. Initial deployment on AWS. Budget for external services is moderate."
    project_technical_vision_for_workflow = "A modular microservices architecture is preferred for scalability. Prioritize user data privacy."

    inputs_for_workflow = {
        "user_idea": simulated_taskmaster_output_as_user_idea,
        "stakeholder_feedback": stakeholder_feedback_notes,
        "market_research_data": market_research_summary,
        "constraints": project_constraints_for_workflow,
        "technical_vision": project_technical_vision_for_workflow
    }

    final_result = run_idea_to_architecture_workflow(inputs_for_workflow)

    print("\n\n########################")
    print("## Workflow Execution Result (from main_workflow.py direct run):")
    print("########################\n")
    if final_result:
        print("Final output from the Idea-to-Architecture crew:")
        print(final_result.raw if hasattr(final_result, 'raw') else str(final_result))
    else:
        print("Idea-to-Architecture Crew produced no output or an error occurred.")
