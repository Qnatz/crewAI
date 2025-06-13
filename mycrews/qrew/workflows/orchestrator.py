from ..project_manager import ProjectStateManager
from .idea_to_architecture_flow import run_idea_to_architecture_workflow
from .crew_lead_workflow import run_crew_lead_workflow
from .subagent_execution_workflow import run_subagent_execution_workflow
from .final_assembly_workflow import run_final_assembly_workflow

class WorkflowOrchestrator:
    def __init__(self, project_name: str):
        self.state = ProjectStateManager(project_name)
        self.workflows = {
            "taskmaster": self.run_taskmaster_workflow,
            "architecture": run_idea_to_architecture_workflow,
            "crew_assignment": run_crew_lead_workflow,
            "subagent_execution": run_subagent_execution_workflow,
            "final_assembly": run_final_assembly_workflow
        }

    def run_taskmaster_workflow(self, inputs: dict):
        """Placeholder for the taskmaster workflow."""
        print(f"Taskmaster workflow executed with inputs: {inputs}")
        # Ensure project_name is passed through if it was in initial_inputs
        # and other workflows might need it directly from this stage's output.
        return {
            "taskmaster_output": "Processed taskmaster details",
            "project_name": inputs.get("project_name", self.state.project_info.get("name"))
        }

    def execute_pipeline(self, initial_inputs: dict):
        resume_point = self.state.resume_point()

        if not resume_point:
            print("Project already completed.")
            self.state.get_summary().print()
            return self.state.get_artifacts()

        print(f"Resuming project at stage: {resume_point}")

        stages = list(self.workflows.keys())

        try:
            start_index = stages.index(resume_point)
        except ValueError:
            print(f"Error: Resume point '{resume_point}' not found in workflow stages. Starting from beginning.")
            start_index = 0
            # Optionally, you might want to reset or flag this unexpected state.
            # For now, we'll just proceed from the first stage.

        for i in range(start_index, len(stages)):
            stage = stages[i]

            # Skip if already completed (e.g. if resume_point logic was adjusted or for safety)
            if self.state.is_completed(stage):
                print(f"Stage {stage} is already marked as completed. Skipping.")
                continue

            self.state.start_stage(stage)

            current_artifacts = self.state.get_artifacts()
            inputs = {**initial_inputs, **current_artifacts}
            # Ensure project_name is available for workflows if they need it
            if "project_name" not in inputs and "name" in self.state.project_info:
                 inputs["project_name"] = self.state.project_info["name"]


            print(f"\nStarting {stage} stage...")
            try:
                result = self.workflows[stage](inputs)
                self.state.complete_stage(stage, artifacts=result)
                print(f"Completed {stage} stage successfully.")
            except Exception as e:
                error_msg = f"Stage {stage} failed: {str(e)}"
                self.state.fail_stage(stage, error_msg)
                print(error_msg)
                import traceback
                traceback.print_exc() # Print full traceback for debugging
                break  # Stop the pipeline on failure

        # After loop, check project status
        if self.state.state["status"] != "failed":
            # Check if all stages were actually completed
            all_stages_completed = all(self.state.is_completed(s) for s in stages)
            if all_stages_completed:
                self.state.finalize_project()
                print("\nProject completed successfully.")
            else:
                # This case might happen if the loop finished but not all stages are done
                # (e.g. if a stage was skipped but wasn't the one that failed)
                # or if resume_point logic needs refinement for edge cases.
                print("\nPipeline execution finished, but not all stages are marked complete and project not failed. Review state.")

        self.state.get_summary().print()
        return self.state.get_artifacts()
