from crewai import Process, Agent, Task # Crew removed
from crewai.project import CrewBase, agent, crew, task

from ..llm_config import default_llm # Corrected path
from ..config import example_summary_validator # Corrected path
from ..validated_crew import ValidatedCrew

# Import the actual web agents
from mycrews.qrew.agents.web import (
    asset_manager_agent,
    dynamic_page_builder_agent,
    static_page_builder_agent
)

@CrewBase
class WebDevelopmentCrew:
    """WebDevelopmentCrew handles all tasks related to web application development."""
    # agents_config = 'config/agents.yaml' # Example path
    # tasks_config = 'config/tasks.yaml'   # Example path

    # Assign imported agents to the crew
    # Note: The @agent decorator is typically used for defining new agents with YAML or inline.
    # Here, we are using pre-defined agent instances.
    # The CrewAI framework expects agents to be part of the self.agents list if using @crew decorator without explicit agent list.
    # A more direct way when using imported agents is to pass them directly to the Crew constructor.
    # For now, let's define them as properties and pass them explicitly.

    @property
    def asset_manager(self) -> Agent:
        return asset_manager_agent

    @property
    def dynamic_page_builder(self) -> Agent:
        return dynamic_page_builder_agent

    @property
    def static_page_builder(self) -> Agent:
        return static_page_builder_agent

    # Define placeholder tasks for now.
    # These would ideally be loaded from YAML files specific to web development tasks
    # and use the above agents.

    @task
    def static_page_creation_task(self) -> Task:
        return Task(
            description="Develop a static information page for {page_topic} including {required_elements}. "
                        "Ensure the page is responsive and uses assets efficiently. "
                        "Input: {page_topic}, {required_elements}, {design_specifications}.",
            expected_output="A complete static HTML page for {page_topic}, with associated CSS and JavaScript, "
                            "validated for responsiveness and asset optimization.",
            # agent=self.static_page_builder() # This would be the ideal assignment
            # For now, let's assign one of the web agents as a placeholder for agent assignment logic
            agent=static_page_builder_agent,
            successCriteria=["Static HTML page complete", "Page responsive", "Assets optimized", "Validation passed"]
        )

    @task
    def dynamic_feature_development_task(self) -> Task:
        return Task(
            description="Implement the dynamic user feature '{feature_name}' which involves {feature_details}. "
                        "This requires frontend logic and interaction with backend API {api_endpoint}. "
                        "Input: {feature_name}, {feature_details}, {api_endpoint}, {ui_mockups}.",
            expected_output="A fully functional dynamic feature '{feature_name}' integrated into the web application, "
                            "with frontend components and API interactions implemented as per specifications.",
            agent=dynamic_page_builder_agent, # Assigning the relevant agent
            successCriteria=["Dynamic feature functional", "Frontend components implemented", "API interactions implemented"]
        )

    @task
    def asset_optimization_task(self) -> Task:
        return Task(
            description="Optimize all static assets (images, scripts, stylesheets) for the section {section_name}. "
                        "This includes compression, minification, and ensuring efficient delivery. "
                        "Input: {section_name}, {asset_paths}.",
            expected_output="Optimized static assets for {section_name}, with a report on improvements achieved. "
                            "Updated references in the codebase if necessary.",
            agent=asset_manager_agent, # Assigning the relevant agent
            successCriteria=["Static assets optimized", "Report on improvements provided", "Codebase references updated"]
        )

    @crew
    def crew(self) -> ValidatedCrew: # Return type changed
        """Creates the Web Development crew"""
        created_crew = ValidatedCrew( # Changed to ValidatedCrew
            agents=[self.asset_manager, self.dynamic_page_builder, self.static_page_builder],
            tasks=self.tasks, # Automatically populated by @task decorator
            process=Process.sequential, # Can be adjusted as needed
            verbose=True,
            llm=default_llm
        )
        created_crew.configure_quality_gate(
            keyword_check=True,
            custom_validators=[example_summary_validator]
        )
        return created_crew

# Example usage (conceptual)
# if __name__ == '__main__':
#     web_crew = WebDevelopmentCrew()
#     inputs = {
#         'page_topic': 'About Us',
#         'required_elements': 'Team bios, company mission',
#         'design_specifications': 'modern_layout_guide.pdf',
#         'feature_name': 'User Dashboard',
#         'feature_details': 'Display user activity and profile settings',
#         'api_endpoint': '/api/v1/dashboard',
#         'ui_mockups': 'dashboard_mockups.fig',
#         'section_name': 'Homepage',
#         'asset_paths': ['/images/hero.jpg', '/js/main.js']
#     }
#     result = web_crew.crew().kickoff(inputs=inputs)
#     print(result)
