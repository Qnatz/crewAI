import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import sys

# Add project root to sys.path to allow imports like mycrews.qrew.main
# This is often needed if tests are run from a different working directory
project_root_for_test = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if project_root_for_test not in sys.path:
    sys.path.insert(0, project_root_for_test)

# Now import the module to be tested
# Assuming main.py is in mycrews/qrew/
from mycrews.qrew import main as qrew_main
from mycrews.qrew.project_manager import ProjectStateManager # Needed for mocking its instances
from mycrews.qrew.workflows.orchestrator import WorkflowOrchestrator # Needed for mocking


class TestDisplayModelStatus(unittest.TestCase):
    @patch('builtins.print')
    def test_display_model_initialization_status_empty(self, mock_print):
        qrew_main.display_model_initialization_status("--- Test Empty ---", [])
        calls = mock_print.call_args_list
        self.assertIn("--- Test Empty ---", calls[0][0][0])
        self.assertIn("No models to display status for in this category.", calls[1][0][0])
        self.assertIn("--------------------", calls[2][0][0]) # Default width

    @patch('builtins.print')
    def test_display_model_initialization_status_single_success(self, mock_print):
        qrew_main.display_model_initialization_status("--- Test Success ---", [("ModelA", True)])
        calls = mock_print.call_args_list
        self.assertIn("--- Test Success ---", calls[0][0][0])
        self.assertIn("ModelA: ✔️", calls[1][0][0])
        self.assertIn("------------------", calls[2][0][0]) # Width of title

    @patch('builtins.print')
    def test_display_model_initialization_status_single_failure(self, mock_print):
        qrew_main.display_model_initialization_status("--- Test Failure ---", [("ModelB", False)])
        calls = mock_print.call_args_list
        self.assertIn("--- Test Failure ---", calls[0][0][0])
        self.assertIn("ModelB: ❌", calls[1][0][0])
        self.assertIn("--------------------", calls[2][0][0]) # Width of title, adjusted if shorter than 20

    @patch('builtins.print')
    def test_display_model_initialization_status_multiple(self, mock_print):
        statuses = [("ModelX", True), ("ModelY", False), ("ModelZ", True)]
        qrew_main.display_model_initialization_status("--- Test Multiple ---", statuses)
        calls = mock_print.call_args_list
        self.assertIn("--- Test Multiple ---", calls[0][0][0])
        self.assertIn("ModelX: ✔️", calls[1][0][0])
        self.assertIn("ModelY: ❌", calls[2][0][0])
        self.assertIn("ModelZ: ✔️", calls[3][0][0])
        self.assertIn("-------------------", calls[4][0][0])


class TestListAvailableProjects(unittest.TestCase):
    # Path to the projects directory, relative to where qrew_main is.
    # qrew_main.project_root should resolve to the /app directory in the sandbox.
    # So, projects_dir_path_base should be 'mycrews/qrew/projects' relative to /app
    # We need to mock os.path.join to correctly use qrew_main.project_root

    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_list_projects_basic(self, mock_path_exists, mock_open_file, mock_listdir, mock_isdir):
        # Simulate the projects directory existing
        mock_isdir.side_effect = lambda path: path.endswith(os.path.join("mycrews", "qrew", "projects")) or \
                                             path.endswith("project_alpha_123") or \
                                             path.endswith("project_beta_456")

        mock_listdir.return_value = ['project_alpha_123', 'project_beta_456', 'not_a_project_file.txt']

        # Mock os.path.exists for state.json files
        def path_exists_side_effect(path):
            if "project_alpha_123" in path and path.endswith("state.json"):
                return True
            if "project_beta_456" in path and path.endswith("state.json"):
                return True
            return False
        mock_path_exists.side_effect = path_exists_side_effect

        # Mock open for reading state.json
        # Project Alpha: state.json with project_name
        # Project Beta: state.json without project_name (should fallback to folder name)
        def open_side_effect(path, mode='r'):
            if "project_alpha_123" in path and path.endswith("state.json"):
                return mock_open(read_data=json.dumps({"project_name": "Alpha Project From State"})).return_value
            elif "project_beta_456" in path and path.endswith("state.json"):
                 # Malformed JSON or missing key
                return mock_open(read_data=json.dumps({"other_key": "some_value"})).return_value
            return mock_open(read_data="").return_value # Default for other files
        mock_open_file.side_effect = open_side_effect

        # We need to ensure qrew_main.project_root is set correctly for the test environment
        # or mock how list_available_projects constructs its path.
        # For simplicity, let's assume qrew_main.project_root is accessible and correct.
        # qrew_main.project_root is defined in main.py as:
        # project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        # In the test, __file__ is different. So we might need to patch project_root in qrew_main
        with patch('mycrews.qrew.main.project_root', project_root_for_test):
            projects = qrew_main.list_available_projects()

        self.assertIn("Alpha Project From State", projects)
        self.assertIn("project_beta_456", projects) # Fallback to folder name
        self.assertNotIn("not_a_project_file.txt", projects)
        self.assertEqual(len(projects), 2)

    @patch('os.path.isdir')
    def test_list_projects_no_project_dir(self, mock_isdir):
        mock_isdir.return_value = False # Simulate projects directory not existing
        with patch('mycrews.qrew.main.project_root', project_root_for_test):
            projects = qrew_main.list_available_projects()
        self.assertEqual(projects, [])

    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('os.path.exists') # To simulate no state.json files
    def test_list_projects_no_state_files(self, mock_path_exists, mock_listdir, mock_isdir):
        mock_isdir.side_effect = lambda path: path.endswith(os.path.join("mycrews", "qrew", "projects")) or \
                                             path.endswith("project_gamma_789")
        mock_listdir.return_value = ['project_gamma_789']
        mock_path_exists.return_value = False # No state.json files exist

        with patch('mycrews.qrew.main.project_root', project_root_for_test):
            projects = qrew_main.list_available_projects()

        self.assertIn("project_gamma_789", projects) # Fallback to folder name
        self.assertEqual(len(projects), 1)


class TestRunQrewInteraction(unittest.TestCase):

    def setUp(self):
        # Common patchers, start them here if they are used across multiple test methods
        # self.patcher_orchestrator = patch('mycrews.qrew.main.WorkflowOrchestrator')
        # self.MockOrchestrator = self.patcher_orchestrator.start()
        # self.mock_orchestrator_instance = self.MockOrchestrator.return_value
        # self.mock_orchestrator_instance.execute_pipeline = MagicMock(return_value={"status": "simulated_success"})
        pass

    def tearDown(self):
        # unittest.mock.patch.stopall() # Stops all patchers started with start()
        pass

    @patch('builtins.print') # To verify output messages
    @patch('builtins.input')
    @patch('mycrews.qrew.main.list_available_projects')
    @patch('mycrews.qrew.main.WorkflowOrchestrator') # Patching the class
    @patch('mycrews.qrew.main.ProjectStateManager') # Patching the class
    def test_run_qrew_new_idea_input(self, MockProjectStateManager, MockWorkflowOrchestrator, mock_list_projects, mock_input, mock_print):
        mock_list_projects.return_value = [] # No existing projects
        mock_input.return_value = "Create a new amazing app"

        # Mock the orchestrator instance and its execute_pipeline method
        mock_orchestrator_instance = MockWorkflowOrchestrator.return_value
        mock_orchestrator_instance.execute_pipeline.return_value = {"status": "simulated_run_complete"}

        # Mock llm_initialization_statuses from llm_config, assuming it's imported by main
        with patch.dict(qrew_main.sys.modules, {'mycrews.qrew.llm_config': MagicMock(llm_initialization_statuses=[])}):
             qrew_main.run_qrew()

        # Assert ProjectStateManager was NOT called before orchestrator (as it's a new project)
        MockProjectStateManager.assert_not_called()

        # Assert WorkflowOrchestrator was initialized with project_name=None
        MockWorkflowOrchestrator.assert_called_once_with(project_name=None)

        # Assert execute_pipeline was called and capture its `pipeline_inputs`
        call_args = mock_orchestrator_instance.execute_pipeline.call_args
        self.assertIsNotNone(call_args)
        pipeline_inputs_received = call_args[0][0]

        self.assertEqual(pipeline_inputs_received.get("user_request"), "Create a new amazing app")
        self.assertIsNone(pipeline_inputs_received.get("project_name")) # Key for new project
        self.assertIn("project_goal", pipeline_inputs_received) # Check some default fields

    @patch('builtins.print')
    @patch('builtins.input')
    @patch('mycrews.qrew.main.list_available_projects')
    @patch('mycrews.qrew.main.WorkflowOrchestrator')
    @patch('mycrews.qrew.main.ProjectStateManager')
    def test_run_qrew_existing_project_selection(self, MockProjectStateManager, MockWorkflowOrchestrator, mock_list_projects, mock_input, mock_print):
        mock_list_projects.return_value = ['project_alpha', 'project_beta']
        mock_input.return_value = "1" # Select 'project_alpha'

        # Configure the mock ProjectStateManager instance
        mock_state_manager_instance = MockProjectStateManager.return_value
        mock_state_manager_instance.state = {
            "project_name": "project_alpha",
            "status": "in-progress",
            "artifacts": {
                "taskmaster": {"refined_brief": "Original idea for alpha"}
            },
            "project_goal": "Goal for alpha"
        }

        mock_orchestrator_instance = MockWorkflowOrchestrator.return_value
        mock_orchestrator_instance.execute_pipeline.return_value = {"status": "simulated_run_complete"}

        with patch.dict(qrew_main.sys.modules, {'mycrews.qrew.llm_config': MagicMock(llm_initialization_statuses=[])}):
            qrew_main.run_qrew()

        # Assert ProjectStateManager was called with 'project_alpha' by main.py
        MockProjectStateManager.assert_called_once_with('project_alpha')

        # Assert WorkflowOrchestrator was initialized with project_name='project_alpha'
        MockWorkflowOrchestrator.assert_called_once_with(project_name='project_alpha')

        pipeline_inputs_received = mock_orchestrator_instance.execute_pipeline.call_args[0][0]
        self.assertEqual(pipeline_inputs_received.get("project_name"), "project_alpha")
        self.assertEqual(pipeline_inputs_received.get("user_request"), "Original idea for alpha")
        self.assertEqual(pipeline_inputs_received.get("project_goal"), "Goal for alpha")
        self.assertEqual(pipeline_inputs_received.get("is_new_project"), False)

    @patch('builtins.print')
    @patch('builtins.input')
    @patch('mycrews.qrew.main.list_available_projects')
    @patch('mycrews.qrew.main.WorkflowOrchestrator')
    @patch('mycrews.qrew.main.ProjectStateManager')
    def test_run_qrew_select_completed_project(self, MockProjectStateManager, MockWorkflowOrchestrator, mock_list_projects, mock_input, mock_print):
        mock_list_projects.return_value = ['completed_project']
        mock_input.return_value = "1"

        mock_state_manager_instance = MockProjectStateManager.return_value
        mock_state_manager_instance.state = {
            "project_name": "completed_project",
            "status": "completed"
        }

        mock_orchestrator_instance = MockWorkflowOrchestrator.return_value

        with patch.dict(qrew_main.sys.modules, {'mycrews.qrew.llm_config': MagicMock(llm_initialization_statuses=[])}):
            qrew_main.run_qrew()

        MockProjectStateManager.assert_called_once_with('completed_project')

        # Assert that a message about completion was printed
        printed_output = "".join(call[0][0] for call in mock_print.call_args_list if call[0]) # Handle empty calls if any
        self.assertIn("Project 'completed_project' is already marked as completed.", printed_output)

        # Assert WorkflowOrchestrator was NOT called to execute pipeline
        mock_orchestrator_instance.execute_pipeline.assert_not_called()
        # Also check if WorkflowOrchestrator constructor was called or not.
        # Based on current main.py, orchestrator is initialized before the completed check leads to return.
        # So, the constructor *would* be called. The important part is execute_pipeline is not.
        MockWorkflowOrchestrator.assert_called_once_with(project_name='completed_project')


    @patch('builtins.print')
    @patch('builtins.input')
    @patch('mycrews.qrew.main.list_available_projects')
    @patch('mycrews.qrew.main.WorkflowOrchestrator')
    @patch('mycrews.qrew.main.ProjectStateManager')
    def test_run_qrew_invalid_project_number_treats_as_new(self, MockProjectStateManager, MockWorkflowOrchestrator, mock_list_projects, mock_input, mock_print):
        mock_list_projects.return_value = ['project_one']
        mock_input.return_value = "99" # Invalid selection number

        mock_orchestrator_instance = MockWorkflowOrchestrator.return_value
        mock_orchestrator_instance.execute_pipeline.return_value = {"status": "simulated_run_complete"}

        with patch.dict(qrew_main.sys.modules, {'mycrews.qrew.llm_config': MagicMock(llm_initialization_statuses=[])}):
            qrew_main.run_qrew()

        # Should not have tried to load a project with ProjectStateManager via main.py's selection logic
        # (Orchestrator might still call it if it gets a project name, but not from main.py's direct selection path)
        # In this case, project_name_for_orchestrator will be None, so PSM won't be called by main.py.
        calls_to_psm_by_main = [call for call in MockProjectStateManager.mock_calls if call[0] == '()'] # Check constructor calls
        # This assertion is tricky because orchestrator itself might call PSM.
        # Focus on what WorkflowOrchestrator was initialized with.

        MockWorkflowOrchestrator.assert_called_once_with(project_name=None) # Treated as new

        pipeline_inputs_received = mock_orchestrator_instance.execute_pipeline.call_args[0][0]
        self.assertEqual(pipeline_inputs_received.get("user_request"), "99") # Input becomes user_request
        self.assertIsNone(pipeline_inputs_received.get("project_name"))


if __name__ == '__main__':
    unittest.main()
