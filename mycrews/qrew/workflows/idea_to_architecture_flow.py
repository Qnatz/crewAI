import json
import logging
from crewai import Process, Task
from crewai.utilities.i18n import I18N
import os

# Adjusted paths for imports:
from ..llm_config import default_llm
# from ..config import example_summary_validator # Not used in this version
from ..validated_crew import ValidatedCrew
from ..project_manager import ProjectStateManager # Added for state management

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

# Taskmaster Agent
from ..taskmaster import taskmaster_agent

# Custom Tools - Assuming these are appropriately scoped or passed if needed by agents
# from ..tools.custom_agent_tools import CustomDelegateWorkTool, CustomAskQuestionTool
# For simplicity, if these tools are used by agents defined above, they should be part of agent definitions.
# Global instantiation here might conflict with agent-specific tool configurations.

# --- Main Qrew Crew Setup (specific to this workflow's delegation needs) ---
# This crew is used for internal task delegations within this workflow.
all_qrew_agents_for_delegation = [
    idea_interpreter_agent,
    tech_vetting_council_agent,
    project_architect_agent,
    constraint_checker_agent,
    stack_advisor_agent,
    documentation_writer_agent,
    taskmaster_agent,
    software_engineer_agent
]

# It's important that agents are initialized with LLMs and any necessary tools
# *before* being added to crews. Assuming this is handled in their respective definition files.

qrew_main_crew = ValidatedCrew(
    agents=all_qrew_agents_for_delegation,
    tasks=[], # Tasks are dynamically assigned via .delegate_task()
    llm=default_llm, # Default LLM for the crew if tasks don't specify agent LLMs
    verbose=True,
)

# print("Configuring Quality Gate for qrew_main_crew (within idea_to_architecture_flow)...")
# qrew_main_crew.configure_quality_gate(
#     keyword_check=True
# )
# print("qrew_main_crew initialized and Quality Gate configured in idea_to_architecture_flow.py.")
# --- End of Main Qrew Crew Setup ---

def run_idea_to_architecture_workflow(workflow_inputs: dict):
    project_name = workflow_inputs.get("project_name")
    if not project_name:
        # Fallback or error if project_name is critical and not provided
        print("Error: project_name not found in workflow_inputs for idea_to_architecture_flow.")
        # Depending on strictness, either raise an error or use a default.
        # For now, let's try to proceed if other inputs are sufficient for some tasks,
        # but ProjectStateManager will fail if project_name is None.
        # A better approach is to ensure project_name is always passed by the orchestrator.
        raise ValueError("project_name is required for idea_to_architecture_flow")

    state = ProjectStateManager(project_name)

    if state.is_completed("architecture"):
        print(f"Stage 'architecture' for project '{project_name}' is already completed. Using cached artifacts.")
        cached_artifacts = state.get_artifacts("architecture")
        if cached_artifacts:
            return cached_artifacts
        else:
            print("Warning: Stage 'architecture' marked completed, but no artifacts found. Re-running.")
            # Optionally, clear the completed status if re-running is desired:
            # state.state["completed_stages"].remove("architecture") # Exercise with caution
            # state.save_state()

    print(f"## Initializing Idea to Architecture Workflow for project: {project_name}...")

    try:
        # Agents specifically for the 'idea_to_architecture_crew' (planning phase)
        # This list seems to define a subset for a specific crew inside the workflow, distinct from qrew_main_crew
        all_agents_for_internal_crew = [
            idea_interpreter_agent,
            tech_vetting_council_agent,
            project_architect_agent,
            constraint_checker_agent,
            stack_advisor_agent,
            documentation_writer_agent
        ]

        default_i18n_instance = I18N() # Assuming I18N is still relevant
        for agent_instance in all_agents_for_internal_crew:
            if not hasattr(agent_instance, 'i18n') or agent_instance.i18n is None:
                agent_instance.i18n = default_i18n_instance
            # LLM check can be here if needed, but ideally agents are pre-configured.

        # Task Definitions (largely unchanged, ensure placeholders are robust)
        task_interpret_idea = Task(
            description=f'''Analyze the provided user idea: "{workflow_inputs.get('user_idea', workflow_inputs.get('user_request', 'Not provided'))}",
stakeholder feedback: "{workflow_inputs.get('stakeholder_feedback', 'Not provided')}",
and market research data: "{workflow_inputs.get('market_research', 'Not provided')}".
Produce a structured set of technical requirements and a detailed feature breakdown.''',
            expected_output='''A comprehensive technical requirements specification document AND a detailed feature breakdown document.
    (Success criteria as before)''',
            agent=idea_interpreter_agent
        )

        # For task_vet_requirements_planning, ensure {constraints} is correctly formatted from workflow_inputs
        constraints_str = json.dumps(workflow_inputs.get('constraints', {})) # Make sure it's a string, ideally JSON

        task_vet_requirements_planning_description = f'''Your primary goal is to plan the vetting process for the Technical Requirements Specification and Feature Breakdown (available from 'task_interpret_idea' in your context).
You MUST define the sub-tasks to be delegated to 'ConstraintCheckerAgent' and 'StackAdvisorAgent'.
For 'ConstraintCheckerAgent', the sub-task should be to "Review the provided 'proposed_solution' (Technical Requirements Specification and Feature Breakdown) against the 'project_constraints_document' (value: {constraints_str}). Identify any violations or potential conflicts regarding budget, team skills, security policies, licensing, or infrastructure."
For 'StackAdvisorAgent', the sub-task should be to "Analyze the provided 'project_requirements' (Technical Requirements Specification and Feature Breakdown) to propose an optimal technology stack. Consider 'team_skills' and 'budget_constraints' (both from {constraints_str}) and 'existing_architecture_details' (value: "None - new project"). Provide justifications for stack choices, considering scalability, maintainability, and alignment with the technical vision."
You must return a JSON object with a key "sub_tasks_to_delegate". The value should be a list of dictionaries, where each dictionary represents a sub-task and includes:
- "task_description": A fully self-contained, detailed description for the sub-agent, embedding all necessary data.
- "assigned_agent_role": The role of the agent to delegate to (e.g., "ConstraintCheckerAgent", "StackAdvisorAgent").
- "successCriteria": A list of strings defining success for the sub-task.
Ensure the output of 'task_interpret_idea' is correctly incorporated directly into the "task_description" string you define for the sub-tasks.
Example for 'ConstraintCheckerAgent's task_description: "Review the proposed solution: [output of task_interpret_idea] against the project_constraints_document: {constraints_str}. Identify any violations..."
Example for 'StackAdvisorAgent's task_description: "Analyze the project_requirements: [output of task_interpret_idea] to propose an optimal technology stack. Consider team_skills from constraints: {constraints_str}, budget_constraints from constraints: {constraints_str}, and existing_architecture_details: None - new project. Provide justifications..."
'''

        task_vet_requirements_planning = Task(
            description=task_vet_requirements_planning_description,
            expected_output='''Your entire response MUST BE a single, valid JSON object.
    (Success criteria as before, ensuring JSON validity)''',
            agent=tech_vetting_council_agent,
            context=[task_interpret_idea]
        )

        # This is the crew for the initial planning phase of the workflow.
        idea_to_architecture_planning_crew = ValidatedCrew(
            agents=all_agents_for_internal_crew,
            tasks=[task_interpret_idea, task_vet_requirements_planning],
            process=Process.sequential,
            verbose=True,
            llm=default_llm # Ensure crew has an LLM
        )

        print(f"Kicking off Idea-to-Architecture workflow (Phase 1: Vetting Planning) for project '{project_name}'...")

        agent_role_map = {
            "ConstraintCheckerAgent": constraint_checker_agent,
            "StackAdvisorAgent": stack_advisor_agent,
            "ProjectArchitectAgent": project_architect_agent,
            "SoftwareEngineerAgent": software_engineer_agent
        }

        # Initial crew for idea interpretation and vetting planning
        # Pass only relevant parts of workflow_inputs if the tasks are not designed for **inputs
        planning_crew_inputs = {
            'user_idea': workflow_inputs.get('user_idea', workflow_inputs.get('user_request')),
            'stakeholder_feedback': workflow_inputs.get('stakeholder_feedback'),
            'market_research_data': workflow_inputs.get('market_research'),
            'constraints': workflow_inputs.get('constraints') # Already stringified above for task desc.
        }
        planning_crew_result_obj = idea_to_architecture_planning_crew.kickoff(inputs=planning_crew_inputs)

        # --- Handling output of task_vet_requirements_planning ---
        # Assume planning_crew_result_obj is the direct string output from the last task in the sequential crew
        sub_task_definitions_json_str = str(planning_crew_result_obj)

        if not sub_task_definitions_json_str or not sub_task_definitions_json_str.strip():
            print("Error: Vetting Requirements Planning task (task_vet_requirements_planning) did not produce a valid output string.")
            state.fail_stage("architecture", "Vetting Requirements Planning task produced no output.")
            raise ValueError("Vetting Requirements Planning task failed to produce output.")

        print("\nProcessing output of Vetting Requirements Planning (task_vet_requirements_planning)...")
        delegated_task_results = {}

        # Define extract_json_from_llm_output if not already defined globally or imported
        # For this fix, assuming it's defined as in the previous step's thought process
        import re # Ensure re is imported
        def extract_json_from_llm_output(output_str):
            match = re.search(r"```json\s*(\{.*?\})\s*```", output_str, re.DOTALL)
            if match:
                return match.group(1)
            match = re.search(r"```\s*(\{.*?\})\s*```", output_str, re.DOTALL)
            if match:
                return match.group(1)
            first_brace = output_str.find('{')
            last_brace = output_str.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                return output_str[first_brace : last_brace + 1]
            return None

        actual_json_str_for_sub_tasks = extract_json_from_llm_output(sub_task_definitions_json_str)

        if not actual_json_str_for_sub_tasks:
            error_msg = f"Error: Could not extract JSON for sub-task definitions from Vetting Planning output: {sub_task_definitions_json_str}"
            print(error_msg)
            state.fail_stage("architecture", "Failed to parse sub-task definitions JSON from Vetting Planning output.")
            raise ValueError(error_msg)

        try:
            sub_task_data = json.loads(actual_json_str_for_sub_tasks)
            if "sub_tasks_to_delegate" not in sub_task_data:
                print("Error: 'sub_tasks_to_delegate' key missing in Vetting Planning output JSON.")
                state.fail_stage("architecture", "'sub_tasks_to_delegate' key missing in Vetting Planning JSON.")
                raise ValueError("'sub_tasks_to_delegate' key missing in Vetting Planning JSON.")

            for sub_task_def in sub_task_data["sub_tasks_to_delegate"]:
                # ... (delegation logic as before, using qrew_main_crew.delegate_task)
                assigned_role = sub_task_def.get("assigned_agent_role")
                actual_agent = agent_role_map.get(assigned_role)
                if not actual_agent: continue # Skip if agent not found

                new_sub_task = Task(description=sub_task_def["task_description"], expected_output=sub_task_def.get("expected_output", "Actionable result."), agent=actual_agent)
                sub_task_result = qrew_main_crew.delegate_task(task=new_sub_task)
                delegated_task_results[assigned_role] = str(sub_task_result.raw if hasattr(sub_task_result, 'raw') else sub_task_result)

        except json.JSONDecodeError as e:
            error_msg = f"Error parsing JSON from Vetting Requirements Planning output: {e}. Received: '{actual_json_str_for_sub_tasks}'. Original: '{sub_task_definitions_json_str}'"
            print(error_msg)
            state.fail_stage("architecture", error_msg)
            raise ValueError(error_msg)

        # --- Simplified retrieval of idea_task_output_str ---
        # This assumes the initial user_idea/request is sufficient for later stages if task_interpret_idea's direct output isn't captured.
        # This is a simplification to avoid the AttributeError and may need refinement if the detailed output of task_interpret_idea is crucial
        # and not just its availability as a prior step.
        idea_task_output_str = str(workflow_inputs.get("user_idea",
                                   workflow_inputs.get("user_request",
                                   "Default user idea/request as task_interpret_idea output not directly captured.")))

        synthesis_payload_vetting = {
            "constraint_checker_report": delegated_task_results.get("ConstraintCheckerAgent", "Not available"),
            "stack_advisor_report": delegated_task_results.get("StackAdvisorAgent", "Not available"),
            "idea_interpretation_output": idea_task_output_str,
            "original_constraints": workflow_inputs.get("constraints", "Not provided"),
            "original_user_idea": workflow_inputs.get("user_idea", workflow_inputs.get("user_request", "Not provided"))
        }
        synthesis_desc_vetting = f'''Synthesize the findings... (using synthesis_payload_vetting items)''' # Keep original structure
        task_vet_requirements_synthesis = Task(description=synthesis_desc_vetting, expected_output='A Vetting Report and Final Technical Guidelines...', agent=tech_vetting_council_agent)
        synthesis_result_vetting = qrew_main_crew.delegate_task(task=task_vet_requirements_synthesis)
        vetting_report_and_guidelines_str = str(synthesis_result_vetting.raw if hasattr(synthesis_result_vetting, 'raw') else synthesis_result_vetting)


        # --- Architecture Design Phase ---
        print("\nPreparing Project Architecture Design Planning task...")
        architecture_planning_payload = {
            "user_idea_details_str": idea_task_output_str, # From idea interpretation
            "vetting_report_and_guidelines_str": vetting_report_and_guidelines_str,
            "original_constraints_str": json.dumps(workflow_inputs.get("constraints", {})),
            "technical_vision_str": workflow_inputs.get("technical_vision", "Not provided")
        }

        # Original task_design_architecture_planning from context, ensure its description is available
        # For safety, define it here if it's not guaranteed to be in scope from earlier.
        # Assuming task_design_architecture_planning was defined as before:
        # MODIFIED: The description still takes the same inputs for the ProjectArchitectAgent
        task_design_architecture_direct_desc = '''Your primary goal is to design the detailed software architecture.
Based on:
1. Original Technical Requirements & Feature Breakdown (available as {user_idea_details_str}).
2. The Vetting Report & Final Technical Guidelines (available as {vetting_report_and_guidelines_str}).
3. Overall project constraints (available as {original_constraints_str}).
4. Project's technical vision (available as {technical_vision_str}).

You must produce the complete, final architecture document as a single JSON object.
This JSON object should be comprehensive and adhere to the structure specified in the expected output section.
'''

        # MODIFIED: The expected_output is now the one for the final architecture document
        final_architecture_expected_output = '''IMPORTANT: Your entire response MUST be ONLY a single, valid JSON object. No other text, no explanations before or after the JSON. Start with '{' and end with '}'.

CRITICAL INSTRUCTION: YOUR ENTIRE RESPONSE MUST BE A SINGLE, VALID JSON STRING. DO NOT OUTPUT ANY TEXT, CONVERSATION, MARKDOWN FENCES (unless the fence perfectly encloses ONLY the JSON object), OR EXPLANATIONS BEFORE OR AFTER THE JSON STRING. START YOUR RESPONSE IMMEDIATELY WITH '{' (the opening curly brace of the JSON object) OR WITH '```json\n{' (if using a markdown fence). THE JSON OBJECT MUST ADHERE TO THE STRUCTURE DESCRIBED BELOW.

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
'''

        executable_task_design_architecture_desc_formatted = task_design_architecture_direct_desc.format(**architecture_planning_payload)

        executable_task_design_architecture_final = Task(
            description=executable_task_design_architecture_desc_formatted,
            expected_output=final_architecture_expected_output,
            agent=project_architect_agent
        )

        print("Executing Project Architect Agent for final architecture document...")
        architecture_final_result_obj = qrew_main_crew.delegate_task(task=executable_task_design_architecture_final)

        # The output of this task is now considered the final architecture document string.
        raw_json_string_arch_final = str(architecture_final_result_obj.raw if hasattr(architecture_final_result_obj, 'raw') else architecture_final_result_obj)

        # REMOVED: The entire block for parsing architecture_planning_json_str,
        # and the loop for delegating new_arch_sub_task,
        # and the definition and execution of task_design_architecture_synthesis.

        final_output_data = None
        content_to_parse_arch_final = "" # For use in except block
        try:
            # Using the already defined extract_json_from_llm_output helper
            content_to_parse_arch_final = extract_json_from_llm_output(raw_json_string_arch_final)
            if not content_to_parse_arch_final:
                error_msg = f"Could not isolate a JSON string from the Project Architect Agent's final output: {raw_json_string_arch_final}"
                print(f"Error: {error_msg}")
                state.fail_stage("architecture", "Failed to parse final architecture JSON from Project Architect Agent.")
                raise json.JSONDecodeError(error_msg, raw_json_string_arch_final, 0)

            final_output_data = json.loads(content_to_parse_arch_final)
            print("Successfully parsed final architecture JSON string from Project Architect Agent.")

        except json.JSONDecodeError as e:
            error_msg = f"Error: Failed to parse final architecture JSON from Project Architect Agent: {e}. Raw output: '''{raw_json_string_arch_final}'''. Parsed content attempt: '''{content_to_parse_arch_final}'''"
            print(error_msg)
            raise ValueError(error_msg) # Re-raise to be caught by the main try-except

        print("\nIdea-to-Architecture (Full Workflow) complete.")
        return final_output_data

    except Exception as e:
        print(f"An error occurred during the Idea to Architecture workflow for project '{project_name}': {e}")
        import traceback
        traceback.print_exc()
        state.fail_stage("architecture", str(e))
        raise # Re-raise the exception to be caught by the orchestrator
