import unittest
from crewAI.qrew.crews.utility_crews.code_writing_crew import CodeWritingCrew

class TestCodeWritingCrew(unittest.TestCase):

    def test_code_writing_crew_instantiation_and_kickoff(self):
        """Test that CodeWritingCrew can be instantiated and kickoff runs without immediate error."""
        try:
            crew_instance = CodeWritingCrew()
        except Exception as e:
            self.fail(f"CodeWritingCrew instantiation failed: {e}")

        # Define dummy inputs for the placeholder tasks
        inputs = {
            'code_requirements': 'a function to add two numbers',
            'code_to_debug': 'def add(a,b): return a-b', # Dummy buggy code
            'issue_description': 'adds incorrectly',
            'code_to_test': 'def add(a,b): return a+b', # Dummy corrected code
            'test_specifications': 'test with positive and negative numbers'
        }

        try:
            result = crew_instance.crew().kickoff(inputs=inputs)
            self.assertIsNotNone(result, "Kickoff returned None, expected some result.")
            print(f"CodeWritingCrew kickoff result: {result}") # Optional
        except Exception as e:
            self.fail(f"CodeWritingCrew kickoff failed: {e}")

if __name__ == '__main__':
    unittest.main()
