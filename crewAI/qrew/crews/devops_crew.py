from crewai import Crew, Process, Agent, Task
from crewai import CrewBase, agent, crew, task

# Import the actual devops agent
from crewAI.qrew.agents.devops import devops_agent

@CrewBase
class DevOpsCrew:
    """DevOpsCrew handles CI/CD, infrastructure, monitoring, and deployment tasks."""

    @property
    def cicd_specialist(self) -> Agent: # Naming the property for clarity within the crew
        return devops_agent

    # Define placeholder tasks for DevOps
    @task
    def ci_cd_pipeline_setup_task(self) -> Task:
        return Task(
            description="Set up a full CI/CD pipeline for the {application_name} using {ci_cd_tool}. "
                        "The pipeline must include stages for building, testing (unit, integration), and deploying to {deployment_environment}. "
                        "Input: {application_name}, {ci_cd_tool}, {repository_url}, {deployment_environment}, {build_script_path}, {test_script_path}.",
            expected_output="A functional CI/CD pipeline configuration for {application_name}. "
                            "A successful run of the pipeline deploying a sample change. "
                            "Documentation on how to trigger and monitor the pipeline.",
            agent=devops_agent
        )

    @task
    def infrastructure_provisioning_task(self) -> Task:
        return Task(
            description="Provision the required infrastructure on {cloud_provider} for the {project_name} using {iac_tool} (e.g., Terraform, CloudFormation). "
                        "Infrastructure components include {list_of_components_needed}. "
                        "Input: {cloud_provider}, {project_name}, {iac_tool}, {list_of_components_needed}, {configuration_details}.",
            expected_output="Infrastructure successfully provisioned on {cloud_provider} as per specifications. "
                            "IaC scripts committed to version control. "
                            "Access details and endpoints documented.",
            agent=devops_agent
        )

    @task
    def monitoring_and_alerting_setup_task(self) -> Task:
        return Task(
            description="Implement a monitoring and alerting system for the {application_name} in the {environment} environment using {monitoring_tool}. "
                        "Set up dashboards for key metrics ({key_metrics_list}) and configure alerts for critical thresholds. "
                        "Input: {application_name}, {environment}, {monitoring_tool}, {key_metrics_list}, {alerting_channels}.",
            expected_output="Monitoring dashboards displaying real-time application metrics. "
                            "Alerting system configured and tested. "
                            "Documentation on accessing dashboards and managing alerts.",
            agent=devops_agent
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DevOps crew"""
        return Crew(
            agents=[self.cicd_specialist], # Using the property name
            tasks=self.tasks, # From @task decorator
            process=Process.sequential,
            verbose=True
        )

# Example usage (conceptual)
# if __name__ == '__main__':
#     devops_crew_instance = DevOpsCrew()
#     inputs = {
#         'application_name': 'QrewApp',
#         'ci_cd_tool': 'GitHub Actions',
#         'repository_url': 'git@github.com:user/qrewapp.git',
#         'deployment_environment': 'staging',
#         'build_script_path': './scripts/build.sh',
#         'test_script_path': './scripts/test.sh',
#         'cloud_provider': 'AWS',
#         'project_name': 'Qrew Platform',
#         'iac_tool': 'Terraform',
#         'list_of_components_needed': 'EC2 instances, RDS database, S3 bucket, ELB',
#         'configuration_details': 'terraform_vars.tfvars',
#         'environment': 'production',
#         'monitoring_tool': 'Prometheus & Grafana',
#         'key_metrics_list': 'CPU utilization, memory usage, request latency, error rates',
#         'alerting_channels': 'Slack, PagerDuty'
#     }
#     result = devops_crew_instance.crew().kickoff(inputs=inputs)
#     print(result)
