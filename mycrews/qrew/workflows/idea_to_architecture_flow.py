import json
import logging
from crewai import Process, Task
from crewai.utilities.i18n import I18N
import os # Included as per prompt, though not directly used in visible logic

# Adjusted paths for imports:
from ..llm_config import default_llm
from ..config import example_summary_validator
from ..validated_crew import ValidatedCrew

# Orchestrator Agents
from ..orchestrators.idea_interpreter_agent.agent import idea_interpreter_agent
from ..orchestrators.tech_vetting_council_agent.agent import tech_vetting_council_agent
from ..orchestrators.project_architect_agent.agent import project_architect_agent

# Tech Stack Committee Agents
from ..orchestrators.tech_stack_committee.constraint_checker_agent.agent import constraint_checker_agent
from ..orchestrators.tech_stack_committee.stack_advisor_agent.agent import stack_advisor_agent
from ..orchestrators.tech_stack_committee.documentation_writer_agent.agent import documentation_writer_agent

# Software Engineer Agent
from ..orchestrators.software_engineer_agent.agent import software_engineer_agent

# Taskmaster Agent (moved as it's part of all_qrew_agents)
from ..taskmaster import taskmaster_agent

# Custom Tools
from ..tools.custom_agent_tools import CustomDelegateWorkTool, CustomAskQuestionTool

# Instantiate custom tools (if they are only used by this workflow)
# Based on current main_workflow.py, these are instantiated globally but seem primarily used by run_idea_to_architecture_workflow
# If they are truly global, they should remain in main_workflow.py and be passed or imported.
# For this refactoring, assuming they are specific enough to move with the workflow or the workflow agents expect them.
custom_delegate_tool = CustomDelegateWorkTool() # This was global, its usage by agents needs care
custom_ask_tool = CustomAskQuestionTool()       # This was global, its usage by agents needs care


# --- Main Qrew Crew Setup (specific to this workflow now) ---
all_qrew_agents = [
    idea_interpreter_agent,
    tech_vetting_council_agent,
    project_architect_agent,
    constraint_checker_agent,
    stack_advisor_agent,
    documentation_writer_agent,
    taskmaster_agent, # taskmaster is part of the global crew for delegation
    software_engineer_agent
]

qrew_main_crew = ValidatedCrew(
    agents=all_qrew_agents, # This crew is used for task delegation inside the workflow
    tasks=[],
    llm=default_llm,
    verbose=True,
)

print("Configuring Quality Gate for qrew_main_crew (within idea_to_architecture_flow)...")
qrew_main_crew.configure_quality_gate(
    keyword_check=True
    # custom_validators=[example_summary_validator] # Temporarily disabled
)
print("qrew_main_crew initialized and Quality Gate configured in idea_to_architecture_flow.py.")
# --- End of Main Qrew Crew Setup ---

def run_idea_to_architecture_workflow(workflow_inputs: dict):
    print("## Initializing Idea to Architecture Workflow Agents & Tasks...")

    # Remove custom tools from tech_vetting_council_agent if they were added globally
    # This logic might need review if tools are handled differently post-refactor
    if hasattr(tech_vetting_council_agent, 'tools') and tech_vetting_council_agent.tools is not None:
        tech_vetting_council_agent.tools = [
            tool for tool in tech_vetting_council_agent.tools
            if not isinstance(tool, (CustomDelegateWorkTool, CustomAskQuestionTool))
        ]
    else:
        tech_vetting_council_agent.tools = []

    # Agents specifically for the 'idea_to_architecture_crew' (planning phase)
    # This list seems to define a subset for a specific crew inside the workflow, distinct from qrew_main_crew
    all_agents_for_internal_crew = [
        idea_interpreter_agent,
        tech_vetting_council_agent,
        project_architect_agent,
        constraint_checker_agent,
        stack_advisor_agent,
        documentation_writer_agent
        # software_engineer_agent is in qrew_main_crew, but not in this internal setup crew.
    ]

    default_i18n_instance = I18N()
    for agent_instance in all_agents_for_internal_crew: # Should this iterate over all_qrew_agents instead or also?
        if not hasattr(agent_instance, 'i18n') or agent_instance.i18n is None:
            agent_instance.i18n = default_i18n_instance
        if not hasattr(agent_instance, 'llm') or agent_instance.llm is None:
            # Agents should ideally be initialized with LLMs.
            # If default_llm is available, it could be assigned here as a fallback.
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
The feature breakdown should detail individual components and user interactions for key features.

Specific success criteria for this output include:
- technical requirements specification created
- feature breakdown document created
- user stories with acceptance criteria included
- functional requirements listed
- non-functional requirements listed
- data requirements identified
- glossary of terms provided''',
        agent=idea_interpreter_agent
    )

    task_vet_requirements_planning = Task(
        description='''Your primary goal is to plan the vetting process for the Technical Requirements Specification and Feature Breakdown (available from 'task_interpret_idea' in your context).
You MUST define the sub-tasks to be delegated to 'ConstraintCheckerAgent' and 'StackAdvisorAgent'.
For 'ConstraintCheckerAgent', the sub-task should be to "Review the provided 'proposed_solution' (Technical Requirements Specification and Feature Breakdown) against the 'project_constraints_document' (value: "{constraints}"). Identify any violations or potential conflicts regarding budget, team skills, security policies, licensing, or infrastructure."
For 'StackAdvisorAgent', the sub-task should be to "Analyze the provided 'project_requirements' (Technical Requirements Specification and Feature Breakdown) to propose an optimal technology stack. Consider 'team_skills' and 'budget_constraints' (both from "{constraints}") and 'existing_architecture_details' (value: "None - new project"). Provide justifications for stack choices, considering scalability, maintainability, and alignment with the technical vision."

You must return a JSON object with a key "sub_tasks_to_delegate". The value should be a list of dictionaries, where each dictionary represents a sub-task and includes:
- "task_description": A fully self-contained, detailed description for the sub-agent, embedding all necessary data (e.g., relevant parts of '{constraints}' or the output of 'task_interpret_idea').
- "assigned_agent_role": The role of the agent to delegate to (e.g., "ConstraintCheckerAgent", "StackAdvisorAgent").
- "successCriteria": A list of strings defining success for the sub-task (e.g., ["violations identified", "compliance report generated"]).
Ensure placeholder values like "{constraints}" and the output of 'task_interpret_idea' are correctly incorporated directly into the "task_description" string you define for the sub-tasks.
Example for 'ConstraintCheckerAgent's task_description: "Review the proposed solution: [output of task_interpret_idea] against the project_constraints_document: [content of {constraints}]. Identify any violations..."
Example for 'StackAdvisorAgent's task_description: "Analyze the project_requirements: [output of task_interpret_idea] to propose an optimal technology stack. Consider team_skills: [extracted from {constraints}], budget_constraints: [extracted from {constraints}], and existing_architecture_details: None - new project. Provide justifications..."
''',
        expected_output='''Your entire response MUST BE a single, valid JSON object.
This JSON object must have a top-level key named "sub_tasks_to_delegate".
The value of "sub_tasks_to_delegate" MUST be a list of JSON objects (dictionaries).
Each dictionary in this list represents a sub-task and MUST include the following keys:
- "task_description": A string containing the fully self-contained, detailed description for the sub-agent.
- "assigned_agent_role": A string indicating the role of the agent to delegate to (e.g., "ConstraintCheckerAgent", "StackAdvisorAgent").
- "successCriteria": A list of strings defining the success criteria for the sub-task.
- Optionally, you may include other relevant keys like "category" if applicable.

IMPORTANT: Ensure correct JSON syntax. This means:
- All keys and string values must be enclosed in double quotes.
- Each key-value pair in an object must be followed by a comma if it is not the last pair in that object.
- Each object in a list must be followed by a comma if it is not the last object in that list.

Example of a single sub-task object within the "sub_tasks_to_delegate" list:
{
  "task_description": "Review the provided 'proposed_solution': [output of task_interpret_idea] against the 'project_constraints_document': {constraints}. Identify violations.",
  "assigned_agent_role": "ConstraintCheckerAgent",
  "successCriteria": ["violations identified", "compliance report generated"],
  "category": "Constraints"
}

If there are multiple sub-task objects in the list, they should be comma-separated. For example:
`[ { ...subtask1... }, { ...subtask2... } ]`

Specific success criteria for this output include:
- Valid JSON object produced as the entire output.
- "sub_tasks_to_delegate" key present with a list value.
- Each item in the list is a dictionary containing "task_description", "assigned_agent_role", and "successCriteria".
- Payloads for sub-tasks correctly structured and self-contained.
- All string values and keys are in double quotes.
- Commas are correctly placed between key-value pairs and list items.
''',
        agent=tech_vetting_council_agent,
        context=[task_interpret_idea]
    )

    task_design_architecture_planning = Task(
        description='''Your primary goal is to PLAN the detailed design of a software architecture.
Based on:
1. Original Technical Requirements & Feature Breakdown (available as {user_idea_details_str}).
2. The Vetting Report & Final Technical Guidelines (available as {vetting_report_and_guidelines_str}).
3. Overall project constraints (available as {original_constraints_str}).
4. Project's technical vision (available as {technical_vision_str}).

You must define the sub-tasks to be delegated for designing various architectural components (e.g., database schema, API design for specific modules, UI component structure).
Return a JSON object with a key "sub_tasks_to_delegate". The value should be a list of dictionaries, where each dictionary represents a sub-task for a component design and includes:
- "task_description": A fully self-contained, detailed description for the component design sub-task, embedding all necessary data (e.g., relevant sections from {user_idea_details_str}, {vetting_report_and_guidelines_str}, etc.).
- "assigned_agent_role": The role of the agent to delegate to (e.g., "BackendDeveloperAgent", "FrontendDeveloperAgent", "DatabaseAdminAgent" - you'll need to decide appropriate roles or use a generic "SoftwareEngineerAgent" if specific roles aren't defined yet).
- "successCriteria": A list of strings defining success for that component design.
Example: {{ "task_description": "Design the detailed database schema for PostgreSQL based on data models found in [specific section of user_idea_details_str] and adhering to guidelines in [specific part of vetting_report_and_guidelines_str]...", "assigned_agent_role": "DatabaseAdminAgent", "successCriteria": ["schema diagram created", "SQL scripts provided"] }}
''',
        expected_output='''A JSON object containing a list under the key "sub_tasks_to_delegate". Each item must be a dictionary with "task_description" (self-contained), "assigned_agent_role", and "successCriteria" for component design sub-tasks.

Specific success criteria for this output include:
- component design sub-tasks defined
- delegation plan for architecture created
- payloads for component tasks structured
- successCriteria for component tasks specified''',
        agent=project_architect_agent
    )

    # This is the crew for the initial planning phase of the workflow.
    idea_to_architecture_planning_crew = ValidatedCrew(
        agents=all_agents_for_internal_crew, # Uses the subset of agents
        tasks=[task_interpret_idea, task_vet_requirements_planning],
        process=Process.sequential,
        verbose=True
    )

    print(f"Kicking off Idea-to-Architecture workflow (Phase 1: Vetting Planning) with inputs: {workflow_inputs}")

    # This agent_role_map is used for delegating tasks via qrew_main_crew
    agent_role_map = {
        "ConstraintCheckerAgent": constraint_checker_agent,
        "StackAdvisorAgent": stack_advisor_agent,
        "ProjectArchitectAgent": project_architect_agent,
        "SoftwareEngineerAgent": software_engineer_agent
    }

    # Initial crew for idea interpretation and vetting planning
    planning_crew_result_obj = idea_to_architecture_planning_crew.kickoff(inputs=workflow_inputs)

    sub_task_definitions_json_str = None
    if hasattr(planning_crew_result_obj, 'raw'):
        sub_task_definitions_json_str = planning_crew_result_obj.raw
    elif hasattr(planning_crew_result_obj, 'tasks') and planning_crew_result_obj.tasks:
        planning_task_output = next((t.output for t in planning_crew_result_obj.tasks if t.description == task_vet_requirements_planning.description), None)
        if planning_task_output and hasattr(planning_task_output, 'raw_output'):
            sub_task_definitions_json_str = planning_task_output.raw_output
        elif planning_task_output:
             sub_task_definitions_json_str = str(planning_task_output)
    else:
        print("Warning: Could not determine the standard way to extract raw output from planning_crew_result_obj. Falling back to string conversion.")
        sub_task_definitions_json_str = str(planning_crew_result_obj)

    if not sub_task_definitions_json_str:
        print("Error: Vetting Requirements Planning task did not produce an output string.")
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
            raise json.JSONDecodeError("No JSON object found in output", sub_task_definitions_json_str, 0)

        if "sub_tasks_to_delegate" not in sub_task_data:
            print("Error: 'sub_tasks_to_delegate' key missing in planning output JSON.")
            print(f"Received JSON: {actual_json_str}")
            return None

        for sub_task_def in sub_task_data["sub_tasks_to_delegate"]:
            print(f"  Preparing sub-task: {sub_task_def.get('task_description', 'No description')[:70]}...")
            assigned_role = sub_task_def.get("assigned_agent_role")
            actual_agent = agent_role_map.get(assigned_role)

            if not actual_agent:
                print(f"    Error: Agent for role '{assigned_role}' not found in agent_role_map. Skipping this sub-task.")
                continue

            expected_output_str = sub_task_def.get("expected_output", "Actionable result for the delegated sub-task.")
            criteria_list = sub_task_def.get("successCriteria", ["output generated"])
            if criteria_list:
                expected_output_str += "\n\nSpecific success criteria for this output include:\n" + "\n".join([f"- {c}" for c in criteria_list])

            new_sub_task = Task(
                description=sub_task_def["task_description"],
                expected_output=expected_output_str,
                agent=actual_agent
            )

            print(f"    Delegating to {actual_agent.role} ({actual_agent.id}) using qrew_main_crew...")
            # IMPORTANT: qrew_main_crew is used here for delegation
            sub_task_result = qrew_main_crew.delegate_task(task=new_sub_task)
            delegated_task_results[assigned_role] = str(sub_task_result.raw if hasattr(sub_task_result, 'raw') else sub_task_result)
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
        "original_user_idea": workflow_inputs.get("user_idea", "User idea not explicitly passed to synthesis payload."),
        "original_constraints": workflow_inputs.get("constraints", "Constraints not explicitly passed to synthesis payload.")
    }

    idea_task_output_str = "Not available from planning_crew_result_obj"
    if hasattr(planning_crew_result_obj, 'tasks') and planning_crew_result_obj.tasks:
        first_task_output = next((t.output for t in planning_crew_result_obj.tasks if t.description == task_interpret_idea.description), None)
        if first_task_output:
            if hasattr(first_task_output, 'raw_output'):
                idea_task_output_str = first_task_output.raw_output
            else:
                idea_task_output_str = str(first_task_output)
        else:
            idea_task_output_str = "Output of task_interpret_idea not found or not in expected format."

    synthesis_payload["idea_interpretation_output"] = idea_task_output_str

    synthesis_desc_vetting = f'''Synthesize the findings from the Constraint Checker and Stack Advisor.
Constraint Checker Report: {synthesis_payload['constraint_checker_report']}
Stack Advisor Report: {synthesis_payload['stack_advisor_report']}
The original technical requirements and feature breakdown were based on: {synthesis_payload['idea_interpretation_output']}
Original project constraints were: {synthesis_payload['original_constraints']}
Original user idea was: {synthesis_payload['original_user_idea']}
Compile a final 'Vetting Report' and a set of 'Final Technical Guidelines'.'''

    task_vet_requirements_synthesis = Task(
        description=synthesis_desc_vetting,
        expected_output='''A Vetting Report and a set of Final Technical Guidelines.
The Vetting Report should summarize: Stack Advisor's evaluation, Constraint Checker's compliance report, and the Tech Vetting Council's final decision/recommendations.
The Final Technical Guidelines should list approved technologies, patterns, or constraints.

Specific success criteria for this output include:
- Vetting Report compiled
- Final Technical Guidelines created
- Stack Advisor evaluation summarized
- Constraint Checker compliance report summarized
- Council recommendations included''',
        agent=tech_vetting_council_agent # This task is run by tech_vetting_council_agent
    )

    print("Executing Vetting Requirements Synthesis task using qrew_main_crew...")
    # IMPORTANT: qrew_main_crew is used here for delegation
    synthesis_result = qrew_main_crew.delegate_task(task=task_vet_requirements_synthesis)
    print(f"Synthesis task completed. Result: {str(synthesis_result)[:100]}...")

    # --- Architecture Design Phase ---
    print("\nPreparing Project Architecture Design Planning task...")

    idea_output_for_arch_planning = idea_task_output_str
    if idea_output_for_arch_planning == "Not available from planning_crew_result_obj" or \
       idea_output_for_arch_planning == "Output of task_interpret_idea not found or not in expected format.":
        idea_output_for_arch_planning = workflow_inputs.get('user_idea', "User idea not available.")

    architecture_planning_payload = {
        "user_idea_details_str": idea_output_for_arch_planning,
        "vetting_report_and_guidelines_str": str(synthesis_result.raw if hasattr(synthesis_result, 'raw') else synthesis_result),
        "original_constraints_str": workflow_inputs["constraints"],
        "technical_vision_str": workflow_inputs["technical_vision"]
    }

    original_planning_desc = task_design_architecture_planning.description
    log = logging.getLogger(__name__)
    try:
        execution_planning_desc = original_planning_desc.format(**architecture_planning_payload)
    except KeyError as e:
        log.error(f"KeyError during description formatting for task_design_architecture_planning: {e}. Payload keys: {architecture_planning_payload.keys()}")
        execution_planning_desc = original_planning_desc

    executable_task_design_architecture_planning = Task(
        description=execution_planning_desc,
        expected_output=task_design_architecture_planning.expected_output,
        agent=project_architect_agent # This task is run by project_architect_agent
    )

    print("Executing Project Architecture Design Planning task using qrew_main_crew...")
    # IMPORTANT: qrew_main_crew is used here for delegation
    architecture_planning_result_obj = qrew_main_crew.delegate_task(
        task=executable_task_design_architecture_planning,
    )
    architecture_planning_json_str = str(architecture_planning_result_obj.raw if hasattr(architecture_planning_result_obj, 'raw') else architecture_planning_result_obj)

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
            actual_agent = agent_role_map.get(assigned_role) # Uses agent_role_map defined in this function
            if not actual_agent:
                print(f"    Warning: Agent for role '{assigned_role}' not found in agent_role_map. Defaulting to SoftwareEngineerAgent.")
                actual_agent = software_engineer_agent # software_engineer_agent must be in scope

            arch_expected_output_str = sub_task_def.get("expected_output", "Detailed design for the architectural component.")
            arch_criteria_list = sub_task_def.get("successCriteria", ["component design completed"])
            if arch_criteria_list:
                arch_expected_output_str += "\n\nSpecific success criteria for this output include:\n" + "\n".join([f"- {c}" for c in arch_criteria_list])

            new_arch_sub_task = Task(
                description=sub_task_def["task_description"],
                expected_output=arch_expected_output_str,
                agent=actual_agent
            )

            print(f"    Delegating architecture sub-task to {actual_agent.role} ({actual_agent.id}) using qrew_main_crew...")
            # IMPORTANT: qrew_main_crew is used here for delegation
            arch_sub_task_result = qrew_main_crew.delegate_task(task=new_arch_sub_task)
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
    architecture_synthesis_payload = {
        "component_design_results": json.dumps(architecture_delegated_task_results),
        "original_user_idea": idea_output_for_arch_planning,
        "vetting_report_and_guidelines": str(synthesis_result.raw if hasattr(synthesis_result, 'raw') else synthesis_result),
        "original_constraints": workflow_inputs["constraints"],
        "technical_vision": workflow_inputs["technical_vision"]
    }

    synthesis_desc_arch = f'''Synthesize all component design outputs into a final, detailed software architecture document.
Component Designs (JSON string): {architecture_synthesis_payload['component_design_results']}
Original Technical Requirements & Feature Breakdown: {architecture_synthesis_payload['original_user_idea']}
Vetting Report & Final Technical Guidelines: {architecture_synthesis_payload['vetting_report_and_guidelines']}
Overall project constraints: {architecture_synthesis_payload['original_constraints']}
Project's technical vision: {architecture_synthesis_payload['technical_vision']}'''

    task_design_architecture_synthesis = Task(
        description=synthesis_desc_arch,
        expected_output='''IMPORTANT: Your entire response MUST be ONLY a single, valid JSON object. No other text, no explanations before or after the JSON. Start with '{' and end with '}'.\n\nCRITICAL INSTRUCTION: YOUR ENTIRE RESPONSE MUST BE A SINGLE, VALID JSON STRING. DO NOT OUTPUT ANY TEXT, CONVERSATION, MARKDOWN FENCES (unless the fence perfectly encloses ONLY the JSON object), OR EXPLANATIONS BEFORE OR AFTER THE JSON STRING. START YOUR RESPONSE IMMEDIATELY WITH '{' (the opening curly brace of the JSON object) OR WITH '```json\n{' (if using a markdown fence). THE JSON OBJECT MUST ADHERE TO THE STRUCTURE DESCRIBED BELOW.

The JSON object you return MUST include the following top-level keys:
- "type": Set this to the string "software".
- "summary": Provide ONLY the comprehensive textual summary of the entire architecture itself. Do NOT include your thought process or plan for generating this summary in this string value. The summary should cover an overview, key decisions, security, cost, CI/CD, monitoring, and any risks or pending items.
- "approved_technologies": A dictionary or list detailing core approved technologies (e.g., frontend, backend, database, infrastructure).
- "pending_decisions": A list of critical decisions that are still unresolved (e.g., specific frameworks, compute services).
- "security_plan_summary": A brief summary of the security implementation plan. Provide ONLY the brief summary text.
- "cost_analysis_summary": A brief summary of the cost analysis and optimization strategies. Provide ONLY the brief summary text.
- "ci_cd_pipeline_summary": A brief summary of the CI/CD automation pipeline design. Provide ONLY the brief summary text.
- "monitoring_strategy_summary": A brief summary of the monitoring strategy. Provide ONLY the brief summary text.
- "backend_spec": A string detailing backend architecture, technologies, APIs, and data models. If not fully detailed, provide a high-level overview and placeholders for further breakdown. Provide ONLY the string detailing the backend architecture. Do not include your plan or thoughts for creating this spec in this value.
- "frontend_spec": A string detailing frontend architecture (e.g., for web or a general placeholder if mobile is separate), technologies, and key UI components. If not fully detailed, provide a high-level overview. Provide ONLY the string detailing the frontend architecture. Do not include your plan or thoughts for creating this spec in this value.
- "mobile_spec": A string detailing mobile architecture (if applicable, otherwise null or a note that it's not in scope), technologies, and key UI components. If not fully detailed, provide a high-level overview. Provide ONLY the string detailing the mobile architecture. Do not include your plan or thoughts for creating this spec in this value.
- "data_model_summary": A brief overview of the data model design. Provide ONLY the brief overview text.
- "api_guidelines_summary": A brief summary of API design guidelines. Provide ONLY the brief summary text.
- "integration_points_summary": A brief summary of key integration points. Provide ONLY the brief summary text.
- "non_functional_requirements_summary": A brief summary of how non-functional requirements are addressed. Provide ONLY the brief summary text.

Ensure the output is a single, valid JSON string.
Specific success criteria for this output include:
- Valid JSON string produced.
- All specified top-level keys are present in the JSON object.
- The "type" field is "software".
- The "summary" field contains a comprehensive textual architectural overview.
- Other fields contain relevant summaries or details as requested.
''',
        agent=project_architect_agent # This task is run by project_architect_agent
    )

    print("Executing Architecture Design Synthesis task using qrew_main_crew...")
    # IMPORTANT: qrew_main_crew is used here for delegation
    architecture_synthesis_result_obj = qrew_main_crew.delegate_task(
        task=task_design_architecture_synthesis,
    )
    print("Architecture Synthesis task completed.")

    final_output_data = None
    raw_json_string = None

    if hasattr(architecture_synthesis_result_obj, 'raw_output') and architecture_synthesis_result_obj.raw_output:
        raw_json_string = architecture_synthesis_result_obj.raw_output
    elif hasattr(architecture_synthesis_result_obj, 'raw') and architecture_synthesis_result_obj.raw:
        raw_json_string = architecture_synthesis_result_obj.raw
    elif isinstance(architecture_synthesis_result_obj, str):
        raw_json_string = architecture_synthesis_result_obj
    else:
        print(f"Warning: Architecture synthesis result is not a string or standard TaskOutput. Type: {type(architecture_synthesis_result_obj)}. Attempting to stringify.")
        raw_json_string = str(architecture_synthesis_result_obj)

    if raw_json_string:
        try:
            content_to_parse = raw_json_string
            md_json_start_index = content_to_parse.find("```json")
            if md_json_start_index != -1:
                temp_str = content_to_parse[md_json_start_index + len("```json"):]
                md_end_index = temp_str.find("```")
                if md_end_index != -1:
                    content_to_parse = temp_str[:md_end_index].strip()
                else:
                    content_to_parse = temp_str.strip()
            else:
                md_code_start_index = content_to_parse.find("```")
                if md_code_start_index != -1:
                    temp_str = content_to_parse[md_code_start_index + len("```"):]
                    md_end_index = temp_str.find("```")
                    if md_end_index != -1:
                        content_to_parse = temp_str[:md_end_index].strip()
                    else:
                        content_to_parse = temp_str.strip()
                else:
                    first_brace = raw_json_string.find('{')
                    last_brace = raw_json_string.rfind('}')
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        content_to_parse = raw_json_string[first_brace : last_brace + 1].strip()
                    else:
                        content_to_parse = raw_json_string.strip()

            if content_to_parse:
                final_output_data = json.loads(content_to_parse)
                print("Successfully parsed architecture synthesis JSON string.")
            else:
                raise json.JSONDecodeError("Could not isolate a non-empty JSON string from the raw output.", raw_json_string, 0)

        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON from architecture synthesis result: {e}")
            print(f"Raw output that failed parsing:\n'''{raw_json_string}'''")
            final_output_data = {
                "error": "Failed to parse architecture JSON",
                "raw_content": raw_json_string,
                "type": "error_parsing_architecture"
            }
        except Exception as e:
            print(f"An unexpected error occurred during JSON parsing of architecture result: {e}")
            final_output_data = {
                "error": f"Unexpected error during JSON parsing: {str(e)}",
                "raw_content": raw_json_string,
                "type": "error_parsing_architecture"
            }
    else:
        print("Error: Architecture synthesis result was empty or None.")
        final_output_data = {
            "error": "Architecture synthesis result was empty",
            "type": "error_empty_architecture_result"
        }

    print("\nIdea-to-Architecture (Full Workflow) complete.")
    return final_output_data

# Note: The if __name__ == "__main__": block from main_workflow.py is NOT moved here.
# That will remain in main_workflow.py to call this refactored function.
