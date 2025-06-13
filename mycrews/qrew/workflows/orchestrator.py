from .idea_to_architecture_flow import run_idea_to_architecture_workflow
from .crew_lead_workflow import run_crew_lead_workflow
from .subagent_execution_workflow import run_subagent_execution_workflow
from .final_assembly_workflow import run_final_assembly_workflow
from ..project_manager import ProjectStateManager # Adjusted import path

class WorkflowOrchestrator:
    def __init__(self, project_name):
        self.state = ProjectStateManager(project_name)
        # The workflow functions themselves are expected to handle their inputs
        # and interact with ProjectStateManager if they need to load/save intermediate artifacts
        # specific to their internal steps, or check if they can be skipped.
        self.workflows = {
            "taskmaster": self.run_taskmaster_workflow, # Placeholder for now
            "architecture": run_idea_to_architecture_workflow,
            "crew_assignment": run_crew_lead_workflow,
            "subagent_execution": run_subagent_execution_workflow,
            "final_assembly": run_final_assembly_workflow
        }

    def run_taskmaster_workflow(self, inputs: dict):
        # This is a placeholder.
        # The actual taskmaster logic might be more complex and involve agent execution.
        # For now, it will simulate completion and potentially return some initial artifact.
        print("Executing Taskmaster workflow (placeholder)...")
        # Example: Taskmaster might define the project scope or initial tasks list
        taskmaster_output = {"initial_brief": inputs.get("user_request", "No user request provided")}
        # In a real scenario, this output would be the result of an agent's work.
        return taskmaster_output

    def execute_pipeline(self, initial_inputs: dict):
        # Add project_name to initial_inputs if not already present,
        # as workflows might need it to initialize their own ProjectStateManager instances
        # if they need to check sub-steps.
        if "project_name" not in initial_inputs and hasattr(self.state, 'project_info'):
            initial_inputs["project_name"] = self.state.project_info.get("name")

        resume_point = self.state.resume_point()

        if resume_point is None and self.state.state.get("status") == "completed":
            print("Project already completed.")
            self.state.get_summary().print()
            return self.state.get_artifacts() # Return all artifacts for a completed project

        if resume_point is None and self.state.state.get("status") != "failed":
            # This means all stages are complete, and project is ready for finalization or is already finalized.
            # If it reached here and not "completed", it means it's ready to be finalized.
            if self.state.state.get("status") != "completed":
                 print("All stages completed. Finalizing project...")
                 self.state.finalize_project()
            self.state.get_summary().print()
            return self.state.get_artifacts()

        print(f"Resuming project at stage: {resume_point if resume_point else 'finalization'}")

        # Define the order of stages
        stages = [
            "taskmaster",
            "architecture",
            "crew_assignment",
            "subagent_execution",
            "final_assembly"
        ]

        start_index = 0
        if resume_point:
            try:
                start_index = stages.index(resume_point)
            except ValueError:
                print(f"Error: Resume point '{resume_point}' not found in defined stages. Starting from beginning.")
                self.state.fail_stage("orchestrator_setup", f"Invalid resume point: {resume_point}")
                # Fall through to print summary and exit

        current_artifacts = self.state.get_artifacts()

        for i in range(start_index, len(stages)):
            stage = stages[i]

            if self.state.is_completed(stage):
                print(f"Stage {stage} already completed. Skipping.")
                continue

            self.state.start_stage(stage)

            try:
                # Prepare inputs: combine initial_inputs with all artifacts collected so far
                inputs_for_stage = {
                    **initial_inputs, # Original inputs provided to the pipeline
                    **current_artifacts # All artifacts from previous stages
                }

                # Add specific artifacts from the immediately preceding stage if needed,
                # though the current structure makes all prior artifacts available.
                # For example, if 'architecture' needs 'taskmaster's output specifically by key:
                # if stage == "architecture" and "taskmaster" in current_artifacts:
                #    inputs_for_stage["taskmaster_output"] = current_artifacts["taskmaster"]

                print(f"\nStarting {stage} stage...")
                # The workflow function for the stage is called.
                # It's responsible for its own logic and returning its artifacts.
                result = self.workflows[stage](inputs_for_stage)

                # Save stage artifacts and update current_artifacts
                self.state.complete_stage(stage, artifacts=result)
                if result: # Merge new artifacts into our collected current_artifacts
                    current_artifacts[stage] = result
                print(f"Completed {stage} stage successfully.")

            except Exception as e:
                error_msg = f"Stage {stage} failed: {str(e)}"
                self.state.fail_stage(stage, error_msg)
                print(error_msg)
                import traceback
                traceback.print_exc() # Print stack trace for debugging
                break # Stop pipeline execution on failure

        # Finalize if all stages completed and project not already marked failed
        if self.state.state["status"] != "failed":
            # Check if all stages in the defined list are now complete
            all_stages_done = all(self.state.is_completed(s) for s in stages)
            if all_stages_done:
                self.state.finalize_project()
                print("Project completed and finalized successfully.")
            else:
                # This case might happen if the loop finished but not all stages were processed
                # (e.g. if break was called from a non-exception path, which it isn't currently)
                # Or if resume_point was None initially but project wasn't 'completed'.
                print("Workflow execution finished, but not all stages were completed. Project not finalized.")

        # Print summary
        self.state.get_summary().print()

        return self.state.get_artifacts() # Return all artifacts, successful or not
