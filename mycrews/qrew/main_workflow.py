from crewai import Crew, Process, Task
from crewai.utilities.i18n import I18N
import os

# Orchestrator Agents
from .orchestrators.idea_interpreter_agent.agent import idea_interpreter_agent
from .orchestrators.tech_vetting_council_agent.agent import tech_vetting_council_agent
from .orchestrators.project_architect_agent.agent import project_architect_agent

# Tech Stack Committee Agents
from .orchestrators.tech_stack_committee.constraint_checker_agent.agent import constraint_checker_agent
from .orchestrators.tech_stack_committee.stack_advisor_agent.agent import stack_advisor_agent
from .orchestrators.tech_stack_committee.documentation_writer_agent.agent import documentation_writer_agent

# Custom Tools
from .tools.custom_agent_tools import CustomDelegateWorkTool, CustomAskQuestionTool

# Instantiate custom tools at module level
custom_delegate_tool = CustomDelegateWorkTool()
custom_ask_tool = CustomAskQuestionTool()

def run_idea_to_architecture_workflow(workflow_inputs: dict):
    print("## Initializing Idea to Architecture Workflow Agents & Tasks...")

    current_tvca_tools = []
    if hasattr(tech_vetting_council_agent, 'tools') and tech_vetting_council_agent.tools is not None:
        current_tvca_tools = [tool for tool in tech_vetting_council_agent.tools if not isinstance(tool, (CustomDelegateWorkTool, CustomAskQuestionTool))]

    current_tvca_tools.extend([custom_delegate_tool, custom_ask_tool])
    tech_vetting_council_agent.tools = current_tvca_tools

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
        agent=idea_interpreter_agent
    )

    task_vet_requirements = Task(
        description='''You have received a Technical Requirements Specification and a Feature Breakdown from the Idea Interpreter Agent (available in your task context).
Your task is to lead the Tech Vetting Council to review these documents thoroughly.
Use the overall project constraints, "{constraints}", to guide your vetting.

You MUST use your 'Delegate Work to Co-worker (Custom)' tool for the following specific delegations:
1.  To 'ConstraintCheckerAgent':
    - The `task` for this delegation should be to "Review the provided Technical Requirements Specification and Feature Breakdown against specific project constraints. Identify any violations or potential conflicts regarding budget, team skills, security policies, licensing, or infrastructure."
    - When calling the tool, for its `inputs` parameter, you should construct a dictionary where you pass the main project constraints. For example: {{"subtask_constraints_input": "{constraints}"}}. The `task` string you provide to the tool for the ConstraintCheckerAgent should then use a placeholder like `{{subtask_constraints_input}}` which will be filled by this `inputs` dictionary.
    - The `context_str` for this delegation should be "Focus on identifying clear violations or risks based on the provided documents and constraints."
2.  To 'StackAdvisorAgent':
    - The `task` for this delegation should be to "Analyze the Technical Requirements Specification and Feature Breakdown to propose an optimal technology stack. Consider team skills (assume 'general full-stack proficiency' if not specified otherwise in requirements) and budget constraints (use the overall project constraints for this, available to you as "{constraints}")."
    - When calling the tool, if you need to pass specific parts of the main "{constraints}" to the StackAdvisor, construct an `inputs` dictionary for the tool call accordingly. For example: `{{"budget_info_for_advisor": "[relevant budget part of {constraints}]"}}` and use `{{budget_info_for_advisor}}` in the `task` string for the StackAdvisor.
    - The `context_str` for this delegation should be "Provide justifications for stack choices, considering scalability, maintainability, and alignment with the technical vision if available."

After receiving reports from both delegated tasks, synthesize their findings, incorporate the council\'s discussion (simulated by your reasoning), and compile a final \'Vetting Report\' and a set of \'Final Technical Guidelines\'.''',
        expected_output='''A Vetting Report and a set of Final Technical Guidelines.
The Vetting Report should summarize:
- Stack Advisor\'s evaluation.
- Constraint Checker\'s compliance report.
- The Tech Vetting Council\'s final decision/recommendations on the proposal.
The Final Technical Guidelines should list any approved technologies, patterns, or constraints affirmed by the council.''',
        agent=tech_vetting_council_agent,
        context=[task_interpret_idea]
    )

    task_design_architecture = Task(
        description='''Your primary goal is to develop a comprehensive software architecture plan. Base your design on:
1. The original Technical Requirements & Feature Breakdown (from \'task_interpret_idea\', available in your context).
2. The Vetting Report & Final Technical Guidelines (from \'task_vet_requirements\', available in your context).
3. The overall project constraints: "{constraints}".
4. The project\'s technical vision: "{technical_vision}".

You must break down the architecture design into logical components and delegate detailed design for these components using your \'Delegate Work to Co-worker (Custom)\' tool.
For example, when delegating "Detailed database schema design":
- The `task` parameter for the tool could be: "Design the detailed database schema for [DB_TYPE_PLACEHOLDER] based on data models in section [SECTION_REF_PLACEHOLDER] of the Technical Requirements. Adhere to guidelines from the Vetting Report." (Use specific placeholders like [DB_TYPE_PLACEHOLDER] that you define).
- The `inputs` parameter for the tool would then be a dictionary you construct by extracting values from your context. For example: `{"DB_TYPE_PLACEHOLDER": "PostgreSQL", "SECTION_REF_PLACEHOLDER": "3.2"}`.
- Use the `prerequisite_task_ids` parameter if a sub-delegatee needs the direct output of another sub-delegated task you previously assigned.
- Use `context_str` for brief, guiding context.

Synthesize all delegated design outputs and your own architectural insights into a final, detailed software architecture document.''',
        expected_output='''A detailed software architecture document, including:
- High-level system diagrams.
- Technology stack recommendations for each component.
- Data model design overview.
- API design guidelines.
- Integration points.
- Non-functional requirements considerations.''',
        agent=project_architect_agent,
        context=[task_interpret_idea, task_vet_requirements]
    )

    idea_to_architecture_crew = Crew(
        agents=all_agents_for_crew,
        tasks=[task_interpret_idea, task_vet_requirements, task_design_architecture],
        process=Process.sequential,
        verbose=True
    )

    print(f"Kicking off Idea-to-Architecture workflow with inputs: {workflow_inputs}")
    result = idea_to_architecture_crew.kickoff(inputs=workflow_inputs)
    return result

if __name__ == "__main__":
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
