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

# Instantiate custom tools
custom_delegate_tool = CustomDelegateWorkTool()
custom_ask_tool = CustomAskQuestionTool()

# --- Configure Agents ---
if not hasattr(tech_vetting_council_agent, 'tools') or tech_vetting_council_agent.tools is None:
    tech_vetting_council_agent.tools = []
if custom_delegate_tool not in tech_vetting_council_agent.tools:
    tech_vetting_council_agent.tools.append(custom_delegate_tool)
if custom_ask_tool not in tech_vetting_council_agent.tools:
    tech_vetting_council_agent.tools.append(custom_ask_tool)

all_agents = [
    idea_interpreter_agent,
    tech_vetting_council_agent,
    project_architect_agent,
    constraint_checker_agent,
    stack_advisor_agent,
    documentation_writer_agent
]

default_i18n = I18N()
for agent_instance in all_agents:
    if not hasattr(agent_instance, 'i18n') or agent_instance.i18n is None:
        agent_instance.i18n = default_i18n
    if not hasattr(agent_instance, 'llm') or agent_instance.llm is None:
        print(f"Warning: Agent {agent_instance.role} appears to be missing an LLM configuration.")

# --- Define Tasks ---

task_interpret_idea = Task(
    description='Analyze the provided user idea: "{user_idea}", stakeholder feedback: "{stakeholder_feedback}", and market research data: "{market_research_data}". Your primary goal is to deeply understand these inputs. Consult the Knowledge Base for any relevant past projects, architectural decisions, or definitions that could clarify or enrich the user\'s concept. Produce a structured set of technical requirements and a detailed feature breakdown. Ensure the technical requirements are clear, testable, and complete. The feature breakdown should detail individual components and user interactions for key features described in the user idea.',
    expected_output='Tech specs and feature breakdown documents.',
    agent=idea_interpreter_agent
)

task_vet_requirements = Task(
    description='You have received a Technical Requirements Specification and a Feature Breakdown from the Idea Interpreter Agent (available in your task context). Your task is to lead the Tech Vetting Council to review these documents thoroughly. Use the overall project constraints: "{constraints}" to guide your vetting. You MUST use your \'Delegate Work to Co-worker (Custom)\' tool for the following specific delegations: 1. Delegate to \'ConstraintCheckerAgent\': - `task`: "Review the provided Technical Requirements Specification and Feature Breakdown against the project constraints: {{constraints_for_checker}}. Identify any violations or potential conflicts regarding budget, team skills, security policies, licensing, or infrastructure." - `inputs`: {{"constraints_for_checker": "{constraints}"}} - `context_str`: "Focus on identifying clear violations or risks based on the provided documents and constraints." 2. Delegate to \'StackAdvisorAgent\': - `task`: "Analyze the Technical Requirements Specification and Feature Breakdown to propose an optimal technology stack. Consider team skills (assume \'general full-stack proficiency\' if not specified otherwise in requirements) and budget constraints (assume \'standard project budget\' unless specific budget constraints are detailed in the requirements or project constraints: {{constraints_for_advisor}})." - `inputs`: {{"constraints_for_advisor": "{constraints}"}} - `context_str`: "Provide justifications for stack choices, considering scalability, maintainability, and alignment with the technical vision if available." After receiving reports from both delegated tasks, synthesize their findings, incorporate the council\'s discussion (simulated by your reasoning), and compile a final \'Vetting Report\' and a set of \'Final Technical Guidelines\'. These guidelines should affirm or refine the technical direction based on the vetting process.',
    expected_output='Vetting Report and Final Technical Guidelines.',
    agent=tech_vetting_council_agent,
    context=[task_interpret_idea]
)

task_design_architecture = Task(
    description='Your primary goal is to develop a comprehensive software architecture plan. Base your design on: 1. The original Technical Requirements & Feature Breakdown (from \'task_interpret_idea\', available in your context). 2. The Vetting Report & Final Technical Guidelines (from \'task_vet_requirements\', available in your context). 3. The overall project constraints: "{constraints}". 4. The project\'s technical vision: "{technical_vision}". You must break down the architecture design into logical components and delegate detailed design for these components using your \'Delegate Work to Co-worker (Custom)\' tool. For example, you might delegate: - Detailed database schema design. - API design for specific microservices. - User authentication and authorization module architecture. When using the \'Delegate Work to Co-worker (Custom)\' tool: - For the `task` parameter: Provide a clear, specific description for the sub-task. Use placeholders like {{placeholder_name}} for any dynamic data. - For the `inputs` parameter: Provide a dictionary to fill in the placeholders in your sub-task description. Extract necessary data from the documents in your context (e.g., specific requirements, guidelines from the vetting report). - For the `prerequisite_task_ids` parameter: If a sub-delegatee needs the direct output of another sub-delegated task you previously assigned and received results for, list the ID of that completed sub-task. (For initial delegations in this task, this might be empty or refer to main prior tasks if tool allows). - For the `context_str` parameter: Provide brief, guiding context or specific instructions for the delegatee. Synthesize all delegated design outputs and your own architectural insights into a final, detailed software architecture document.',
    expected_output='Detailed software architecture document.',
    agent=project_architect_agent,
    context=[task_interpret_idea, task_vet_requirements]
)

# --- Create and Run Crew ---
idea_to_architecture_crew = Crew(
    agents=all_agents,
    tasks=[task_interpret_idea, task_vet_requirements, task_design_architecture],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    print("## Starting Idea to Architecture Workflow")

    initial_user_idea = "Develop a market-leading application for interactive pet training that is fun and engaging. It should include video streaming, progress tracking, and social sharing features. We want it to be scalable and secure."
    stakeholder_feedback_notes = "User retention is key. Gamification might be important. Mobile-first approach preferred."
    market_research_summary = "Competitors X and Y lack real-time interaction. Users want personalized training plans."
    project_constraints = "Team has strong Python and React skills. Initial deployment on AWS. Budget for external services is moderate."
    project_technical_vision = "A modular microservices architecture is preferred for scalability. Prioritize user data privacy."

    inputs = {
        "user_idea": initial_user_idea,
        "stakeholder_feedback": stakeholder_feedback_notes, # Will be available if task_interpret_idea's description uses it
        "market_research_data": market_research_summary, # Same as above
        "constraints": project_constraints,
        "technical_vision": project_technical_vision
    }

    print(f"\nKicking off crew with inputs: {inputs}")

    result = idea_to_architecture_crew.kickoff(inputs=inputs)

    print("\n\n########################")
    print("## Workflow Execution Result:")
    print("########################\n")
    if result:
        print("Final output from the crew (Project Architect's Software Architecture Document):")
        # Assuming result is the TaskOutput object from the last task, which has a 'raw' attribute
        # If result is the CrewOutput object (from crew.kickoff_for_output), it might be different.
        # For now, let's assume it's compatible with .raw or directly stringable.
        if hasattr(result, 'raw') and result.raw is not None:
            print(result.raw)
        else:
            print(str(result)) # Fallback to string representation
    else:
        print("No result returned or an error occurred during crew execution.")
