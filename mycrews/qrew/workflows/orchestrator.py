from .idea_to_architecture_flow import run_idea_to_architecture_workflow
from .code_implementation_workflow import run_code_implementation_workflow

class WorkflowOrchestrator:
    def __init__(self):
        self.workflows = {
            "idea_to_architecture": run_idea_to_architecture_workflow,
            "code_implementation": run_code_implementation_workflow
            # Future workflows can be added here
        }

    def execute_workflow(self, workflow_name: str, inputs: dict):
        if workflow_name in self.workflows:
            print(f"\n[Orchestrator] Executing workflow: {workflow_name}")
            workflow_function = self.workflows[workflow_name]
            result = workflow_function(inputs)
            print(f"[Orchestrator] Workflow {workflow_name} completed.")
            return result
        raise ValueError(f"Unknown workflow: {workflow_name}")

    def execute_pipeline(self, pipeline: list, initial_inputs: dict):
        results = {}
        current_inputs = initial_inputs.copy() # Start with a copy of initial inputs

        print(f"\n[Orchestrator] Starting pipeline execution with initial input keys: {list(initial_inputs.keys())}")

        for step_index, step in enumerate(pipeline):
            workflow_name = step["name"]
            # Default output_key to workflow_name if not specified in the pipeline step
            output_key = step.get("output_key", workflow_name)

            print(f"\n[Orchestrator] --- Pipeline Step {step_index + 1}: {workflow_name} (output key: {output_key}) ---")
            # To avoid overly verbose logs, we won't print all current_inputs content here unless debugging.
            # print(f"[Orchestrator] Input keys for step {workflow_name}: {list(current_inputs.keys())}")

            try:
                # Execute the workflow with the current accumulated inputs
                result = self.execute_workflow(workflow_name, current_inputs)

                # Store the result of the current step in the main results dictionary
                results[output_key] = result

                # Add/update the result in current_inputs for the next step.
                # This makes the output of this step available to the next step
                # under current_inputs[output_key].
                current_inputs[output_key] = result

                # print(f"[Orchestrator] Stored result for {workflow_name} under key '{output_key}'.")
                # print(f"[Orchestrator] Updated input keys for next step: {list(current_inputs.keys())}")

            except Exception as e:
                error_message = f"Error executing workflow {workflow_name} in pipeline: {e}"
                print(f"[Orchestrator] {error_message}")
                # Store error information in results
                results[output_key] = {"error": str(e), "workflow": workflow_name, "details": "Pipeline execution halted."}
                print(f"[Orchestrator] Pipeline execution halted due to error in {workflow_name}.")
                break # Stop pipeline on error

        print("\n[Orchestrator] Pipeline execution finished.")
        return results

# Example usage:
# orchestrator = WorkflowOrchestrator()
# pipeline = [
#     {"name": "idea_to_architecture"},
#     # 'input_map' is illustrative of a more complex setup, not used by this execute_pipeline
#     {"name": "code_implementation", "input_map": {"architecture": "idea_to_architecture"}}
# ]
# # Example: initial_inputs = {"user_idea": "Build a thing"}
# # results = orchestrator.execute_pipeline(pipeline, initial_inputs)
