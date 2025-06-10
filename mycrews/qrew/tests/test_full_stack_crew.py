import unittest
from crewAI.qrew.crews.full_stack_crew import FullStackCrew

class TestFullStackCrew(unittest.TestCase):

    def test_full_stack_crew_instantiation_and_kickoff(self):
        """Test that the refactored FullStackCrew can be instantiated and kickoff runs."""
        try:
            crew_instance = FullStackCrew()
        except Exception as e:
            self.fail(f"FullStackCrew instantiation failed: {e}")

        # Updated dummy inputs for the refactored FullStackCrew tasks
        inputs = {
            'feature_name': 'User Profile Page V2',
            'feature_requirements': 'Display user details, activity feed, and allow editing profile information.',
            'api_design_guidelines': 'RESTful, use OpenAPI spec v3.',
            'data_requirements': 'User table needs new fields: bio (TEXT), profile_picture_url (VARCHAR). Activity table for feed.',
            'current_database_schema_info': 'Link to current schema dump or ERD.',
            'ui_ux_specifications': 'Link to Figma designs for Profile Page V2.',
            'api_endpoint_details_for_feature': 'Endpoints: GET /users/{id}, PUT /users/{id}, GET /users/{id}/activity',
            'coding_task_description': 'Create a Python script to seed sample user activity data.',
            'relevant_code_files': 'user_model.py, activity_model.py',
            'test_plan_document_url': 'Link to E2E test plan for Profile Page V2.',
            'user_stories_for_feature': 'As a user, I can view my profile. As a user, I can edit my bio.'
        }

        try:
            result = crew_instance.crew().kickoff(inputs=inputs)
            self.assertIsNotNone(result, "Kickoff returned None, expected some result.")
            # print(f"FullStackCrew kickoff result: {result}") # Optional
        except Exception as e:
            # If there's an LLM connectivity issue or API key issue, this might fail.
            # For a structural test, we are primarily concerned with instantiation and task assignment.
            # However, a failing kickoff is still a failing test.
            self.fail(f"FullStackCrew kickoff failed: {e}")

if __name__ == '__main__':
    unittest.main()
