from .idea_to_architecture_flow import run_idea_to_architecture_workflow
from .crew_lead_workflow import run_crew_lead_workflow
from .subagent_execution_workflow import run_subagent_execution_workflow
from .final_assembly_workflow import run_final_assembly_workflow

class WorkflowOrchestrator:
    def __init__(self):
        self.workflows = {
            "idea_to_architecture": run_idea_to_architecture_workflow,
            "crew_lead": run_crew_lead_workflow,
            "subagent_execution": run_subagent_execution_workflow,
            "final_assembly": run_final_assembly_workflow
        }

    def execute_pipeline(self, initial_inputs: dict):
        # Main architectural design
        arch_result = self.workflows["idea_to_architecture"](initial_inputs)

        # Pass to crew leads
        crew_lead_inputs = {
            "architecture": arch_result,
            **initial_inputs
        }
        crew_lead_result = self.workflows["crew_lead"](crew_lead_inputs)

        # Pass to subagents
        subagent_inputs = {
            "crew_assignments": crew_lead_result,
            "architecture": arch_result,
            **initial_inputs
        }
        subagent_result = self.workflows["subagent_execution"](subagent_inputs)

        # Final assembly
        assembly_inputs = {
            "components": subagent_result,
            "architecture": arch_result,
            **initial_inputs
        }
        final_result = self.workflows["final_assembly"](assembly_inputs)

        return {
            "architecture": arch_result,
            "crew_assignments": crew_lead_result,
            "components": subagent_result,
            "final_output": final_result
        }
