import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys

# Add project root for imports
project_root_for_test = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if project_root_for_test not in sys.path:
    sys.path.insert(0, project_root_for_test)

from mycrews.qrew.workflows.orchestrator import WorkflowOrchestrator
from mycrews.qrew.project_manager import ProjectStateManager

class TestWorkflowOrchestratorLogic(unittest.TestCase):

    @patch('mycrews.qrew.workflows.orchestrator.ProjectStateManager')
    @patch('mycrews.qrew.workflows.orchestrator.run_idea_to_architecture_workflow', return_value={"arch_output": "done"})
    @patch('mycrews.qrew.workflows.orchestrator.run_tech_vetting_workflow', return_value={"tech_vetting_output": "done"})
    @patch('mycrews.qrew.workflows.orchestrator.run_crew_lead_workflow', return_value={"crew_lead_output": "done"}) # Mock other stages
    @patch('mycrews.qrew.workflows.orchestrator.run_subagent_execution_workflow', return_value={"subagent_exec_output": "done"})
    @patch('mycrews.qrew.workflows.orchestrator.run_final_assembly_workflow', return_value={"final_output": "done"})
    def test_execute_pipeline_tech_vetting_path(self,
                                                mock_final_assembly, mock_subagent_exec, mock_crew_lead,
                                                mock_tech_vetting, mock_architecture, MockPSM):

        # Mock ProjectStateManager instance and its methods
        mock_psm_instance = MockPSM.return_value
        mock_psm_instance.state = {"status": "new"} # Simulate a new project state initially
        mock_psm_instance.is_completed.return_value = False
        mock_psm_instance.get_artifacts.return_value = {} # No existing artifacts initially

        orchestrator = WorkflowOrchestrator() # Test with orchestrator determining project name

        # Mock taskmaster workflow part of the orchestrator
        mock_taskmaster_output = {
            "project_name": "TestProjectTechVetting",
            "refined_brief": "Brief for tech vetting path.",
            "is_new_project": True,
            "recommended_next_stage": "tech_vetting"
        }
        orchestrator.run_taskmaster_workflow = MagicMock(return_value=mock_taskmaster_output)

        initial_inputs = {"user_request": "test request for tech vetting"}
        orchestrator.execute_pipeline(initial_inputs)

        # Check that ProjectStateManager was initialized with the project name from taskmaster
        MockPSM.assert_called_with("TestProjectTechVetting")

        # Check that taskmaster was called (implicitly via execute_pipeline's internal logic)
        orchestrator.run_taskmaster_workflow.assert_called_once_with(initial_inputs)
        mock_psm_instance.complete_stage.assert_any_call("taskmaster", artifacts=mock_taskmaster_output)

        # Check that tech_vetting workflow was called
        mock_tech_vetting.assert_called_once()
        # Inputs to tech_vetting should include taskmaster outputs
        args_tech_vetting, _ = mock_tech_vetting.call_args
        self.assertIn("taskmaster", args_tech_vetting[0])
        self.assertEqual(args_tech_vetting[0]["taskmaster"]["project_name"], "TestProjectTechVetting")
        mock_psm_instance.complete_stage.assert_any_call("tech_vetting", artifacts={"tech_vetting_output": "done"})

        # Check that architecture workflow was called
        mock_architecture.assert_called_once()
        args_architecture, _ = mock_architecture.call_args
        self.assertIn("taskmaster", args_architecture[0])
        self.assertIn("tech_vetting", args_architecture[0]) # Ensure tech_vetting artifacts are passed
        self.assertEqual(args_architecture[0]["tech_vetting"]["tech_vetting_output"], "done")
        mock_psm_instance.complete_stage.assert_any_call("architecture", artifacts={"arch_output": "done"})

        # Check other stages were called
        mock_crew_lead.assert_called_once()
        mock_subagent_exec.assert_called_once()
        mock_final_assembly.assert_called_once()


    @patch('mycrews.qrew.workflows.orchestrator.ProjectStateManager')
    @patch('mycrews.qrew.workflows.orchestrator.run_idea_to_architecture_workflow', return_value={"arch_output": "done"})
    @patch('mycrews.qrew.workflows.orchestrator.run_tech_vetting_workflow', return_value={"tech_vetting_output": "done"})
    @patch('mycrews.qrew.workflows.orchestrator.run_crew_lead_workflow', return_value={"crew_lead_output": "done"})
    @patch('mycrews.qrew.workflows.orchestrator.run_subagent_execution_workflow', return_value={"subagent_exec_output": "done"})
    @patch('mycrews.qrew.workflows.orchestrator.run_final_assembly_workflow', return_value={"final_output": "done"})
    def test_execute_pipeline_direct_to_architecture_path(self,
                                                        mock_final_assembly, mock_subagent_exec, mock_crew_lead,
                                                        mock_tech_vetting, mock_architecture, MockPSM):

        mock_psm_instance = MockPSM.return_value
        mock_psm_instance.state = {"status": "new"}
        mock_psm_instance.is_completed.return_value = False
        mock_psm_instance.get_artifacts.return_value = {}

        orchestrator = WorkflowOrchestrator()

        mock_taskmaster_output = {
            "project_name": "TestProjectArchitecture",
            "refined_brief": "Brief for direct architecture path.",
            "is_new_project": True,
            "recommended_next_stage": "architecture"
        }
        orchestrator.run_taskmaster_workflow = MagicMock(return_value=mock_taskmaster_output)

        initial_inputs = {"user_request": "test request for architecture"}
        orchestrator.execute_pipeline(initial_inputs)

        MockPSM.assert_called_with("TestProjectArchitecture")
        orchestrator.run_taskmaster_workflow.assert_called_once_with(initial_inputs)
        mock_psm_instance.complete_stage.assert_any_call("taskmaster", artifacts=mock_taskmaster_output)

        # Check that tech_vetting workflow was NOT called
        mock_tech_vetting.assert_not_called()

        # Check that architecture workflow was called
        mock_architecture.assert_called_once()
        args_architecture, _ = mock_architecture.call_args
        self.assertIn("taskmaster", args_architecture[0])
        self.assertNotIn("tech_vetting", args_architecture[0]) # Ensure tech_vetting artifacts are NOT passed
        mock_psm_instance.complete_stage.assert_any_call("architecture", artifacts={"arch_output": "done"})

        mock_crew_lead.assert_called_once()
        mock_subagent_exec.assert_called_once()
        mock_final_assembly.assert_called_once()

if __name__ == '__main__':
    unittest.main()
