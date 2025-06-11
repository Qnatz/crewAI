import json # Added for parsing sub-task definitions
from crewai import Process, Task # Crew removed from here
from crewai.utilities.i18n import I18N
import os
from .llm_config import default_llm # Added for qrew_main_crew
from .config import example_summary_validator # Imported validator
from .validated_crew import ValidatedCrew # Added ValidatedCrew import
# from crewai import Task # Added for the validator's type hint - already imported

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

You must return a JSON object with a key "sub_tasks_to_delegate". The value should be a list of dictionaries, where each dictionary represents a sub-task and includes:
- "task_description": The detailed description for the sub-agent.
- "assigned_agent_role": The role of the agent to delegate to (e.g., "ConstraintCheckerAgent", "StackAdvisorAgent").
- "payload": A dictionary containing all necessary data for the sub-task (e.g., {"project_constraints_document": "...", "proposed_solution": "..."}).
- "successCriteria": A list of strings defining success for the sub-task (e.g., ["violations identified", "compliance report generated"]).
Ensure placeholder values like "{constraints}" and the output from 'task_interpret_idea' are correctly incorporated into the descriptions and payloads you define for the sub-tasks.
The output of 'task_interpret_idea' will be available in your context. Access its content as needed to formulate the 'payload' for the sub-tasks.
Example for 'ConstraintCheckerAgent' payload: {"project_constraints_document": "{constraints}", "proposed_solution": "{task_interpret_idea.output}"}
Example for 'StackAdvisorAgent' payload: {"project_requirements": "{task_interpret_idea.output}", "team_skills": "Extract from {constraints}", "budget_constraints": "Extract from {constraints}", "existing_architecture_details": "None - new project"}
''',
        expected_output='''A JSON object containing a list under the key "sub_tasks_to_delegate". Each item in the list must be a dictionary with "task_description", "assigned_agent_role", "payload", and "successCriteria" for the sub-tasks intended for ConstraintCheckerAgent and StackAdvisorAgent.''',
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
Return a JSON object with a key "sub_tasks_to_delegate". The value should be a list of dictionaries, where each dictionary represents a sub-task for a component design and includes:
- "task_description": Detailed description for the component design sub-task.
- "assigned_agent_role": The role of the agent to delegate to (e.g., "BackendDeveloperAgent", "FrontendDeveloperAgent", "DatabaseAdminAgent" - you'll need to decide appropriate roles or use a generic "SoftwareEngineerAgent" if specific roles aren't defined yet).
- "payload": A dictionary containing all necessary data for the sub-task.
- "successCriteria": A list of strings defining success for that component design.
Example: { "task_description": "Design the detailed database schema for PostgreSQL based on data models...", "assigned_agent_role": "DatabaseAdminAgent", "payload": {...}, "successCriteria": ["schema diagram created", "SQL scripts provided"] }
''',
        expected_output='''A JSON object containing a list under the key "sub_tasks_to_delegate". Each item must be a dictionary with "task_description", "assigned_agent_role", "payload", and "successCriteria" for component design sub-tasks.''',
        agent=project_architect_agent, # Assigned to Project Architect
        # Context will be implicitly handled by the payload constructed during execution
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

    # Extracting the raw output string from the planning task.
    # This assumes the last task in the sequential crew is task_vet_requirements_planning.
    # Adjust if CrewAI's kickoff result structure is different or if a specific task output is needed.
    sub_task_definitions_json_str = None
    if hasattr(planning_crew_result_obj, 'raw'): # Common for single task output or final raw output
        sub_task_definitions_json_str = planning_crew_result_obj.raw
    elif hasattr(planning_crew_result_obj, 'tasks') and planning_crew_result_obj.tasks:
        # If kickoff returns a result object with a list of task outputs
        # Find the output of task_vet_requirements_planning
        planning_task_output = next((t.output for t in planning_crew_result_obj.tasks if t.description == task_vet_requirements_planning.description), None)
        if planning_task_output and hasattr(planning_task_output, 'raw_output'):
            sub_task_definitions_json_str = planning_task_output.raw_output
        elif planning_task_output: # Fallback if raw_output is not present but output itself might be the string
             sub_task_definitions_json_str = str(planning_task_output) # Convert to string if it's an object
    else: # Fallback if the structure is unexpected
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

            # Ensure payload is a dictionary, even if not provided or malformed
            payload = sub_task_def.get("payload")
            if not isinstance(payload, dict):
                print(f"    Warning: Payload for sub-task '{sub_task_def.get('task_description')}' is not a dictionary or missing. Using empty dict. Payload was: {payload}")
                payload = {}

            new_sub_task = Task(
                description=sub_task_def["task_description"],
                expected_output=sub_task_def.get("expected_output", "Actionable result for the delegated sub-task."),
                agent=actual_agent,
                payload=payload,
                successCriteria=sub_task_def.get("successCriteria", ["output generated"]),
            )

            print(f"    Delegating to {actual_agent.role} ({actual_agent.id}) using qrew_main_crew...")
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

    # Retrieving output from task_interpret_idea for context, if available and kickoff result is structured
    # This is a more robust way if planning_crew_result_obj is a rich object
    idea_task_output_str = "Not available from planning_crew_result_obj"
    if hasattr(planning_crew_result_obj, 'tasks') and planning_crew_result_obj.tasks:
        # Ensure there's at least one task and its output is accessible
        if planning_crew_result_obj.tasks[0].output:
            idea_task_output = next((t.output for t in planning_crew_result_obj.tasks if t.description == task_interpret_idea.description), None)
            if idea_task_output and hasattr(idea_task_output, 'raw_output'):
                idea_task_output_str = idea_task_output.raw_output
            elif idea_task_output: # Fallback if raw_output is not present
                idea_task_output_str = str(idea_task_output)
        else:
            idea_task_output_str = "Output of task_interpret_idea not found or not in expected format."

    synthesis_payload["idea_interpretation_output"] = idea_task_output_str


    task_vet_requirements_synthesis = Task(
        description=f'''Synthesize the findings from the Constraint Checker and Stack Advisor.
Constraint Checker Report: {{constraint_checker_report}}
Stack Advisor Report: {{stack_advisor_report}}
The original technical requirements and feature breakdown were based on: {{idea_interpretation_output}}
Original project constraints were: {{original_constraints}}
Original user idea was: {{original_user_idea}}
Compile a final 'Vetting Report' and a set of 'Final Technical Guidelines'.''',
        expected_output='''A Vetting Report and a set of Final Technical Guidelines.
The Vetting Report should summarize: Stack Advisor's evaluation, Constraint Checker's compliance report, and the Tech Vetting Council's final decision/recommendations.
The Final Technical Guidelines should list approved technologies, patterns, or constraints.''',
        agent=tech_vetting_council_agent,
        payload=synthesis_payload,
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

    # Determine the source for idea_interpretation_output for the payload
    # Prefer the more robust extraction if available, otherwise use workflow_inputs as fallback
    idea_output_for_arch_planning = idea_task_output_str # From previous extraction attempt
    if idea_output_for_arch_planning == "Not available from planning_crew_result_obj" or \
       idea_output_for_arch_planning == "Output of task_interpret_idea not found or not in expected format.":
        idea_output_for_arch_planning = workflow_inputs.get('user_idea', "User idea not available.")


    architecture_planning_payload = {
        "user_idea_details_str": idea_output_for_arch_planning,
        "vetting_report_and_guidelines_str": str(synthesis_result.raw if hasattr(synthesis_result, 'raw') else synthesis_result),
        "original_constraints_str": workflow_inputs["constraints"],
        "technical_vision_str": workflow_inputs["technical_vision"]
    }
    # The task_design_architecture_planning object is defined at the module level.
    # We assign its payload here before execution.
    task_design_architecture_planning.payload = architecture_planning_payload

    print("Executing Project Architecture Design Planning task using qrew_main_crew...")
    architecture_planning_result_obj = qrew_main_crew.delegate_task(
        task=task_design_architecture_planning,
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
            # Use ProjectArchitectAgent as a fallback if a specific role is not in agent_role_map
            actual_agent = agent_role_map.get(assigned_role, project_architect_agent)
            if actual_agent == project_architect_agent and assigned_role not in agent_role_map:
                 print(f"    Warning: Agent for role '{assigned_role}' not found. Assigning to ProjectArchitectAgent.")

            payload_arch = sub_task_def.get("payload")
            if not isinstance(payload_arch, dict):
                print(f"    Warning: Payload for arch sub-task '{sub_task_def.get('task_description')}' is not a dictionary or missing. Using empty dict. Payload was: {payload_arch}")
                payload_arch = {}

            new_arch_sub_task = Task(
                description=sub_task_def["task_description"],
                expected_output=sub_task_def.get("expected_output", "Detailed design for the architectural component."),
                agent=actual_agent,
                payload=payload_arch,
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
    architecture_synthesis_payload = {
        "component_design_results": json.dumps(architecture_delegated_task_results), # Pass results as JSON string
        "original_user_idea": idea_output_for_arch_planning,
        "vetting_report_and_guidelines": str(synthesis_result.raw if hasattr(synthesis_result, 'raw') else synthesis_result),
        "original_constraints": workflow_inputs["constraints"],
        "technical_vision": workflow_inputs["technical_vision"]
    }

    task_design_architecture_synthesis = Task(
        description=f'''Synthesize all component design outputs into a final, detailed software architecture document.
Component Designs (JSON string): {{component_design_results}}
Original Technical Requirements & Feature Breakdown: {{original_user_idea}}
Vetting Report & Final Technical Guidelines: {{vetting_report_and_guidelines}}
Overall project constraints: {{original_constraints}}
Project's technical vision: {{technical_vision}}''',
        expected_output='''A detailed software architecture document, including: High-level system diagrams, Technology stack recommendations for each component, Data model design overview, API design guidelines, Integration points, Non-functional requirements considerations.''',
        agent=project_architect_agent,
        payload=architecture_synthesis_payload,
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
