from crewai import Crew, Task
# Adjust the import path for CodeWriterAgent based on its actual location
from q_ware.agents.dev_utilities.code_writer_agent.agent import code_writer_agent # Assuming instance is exported

# Per user feedback, CrewAI agents are typically instantiated.
# The imported `code_writer_agent` is an instance.
# If the user meant to import the class `CodeWriterAgent` and instantiate it here,
# the import would be: from q_ware.agents.dev_utilities.code_writer_agent.agent import CodeWriterAgent
# and then CodeWriterAgent() would be used below.
# For now, assuming the exported `code_writer_agent` instance is what's intended for use.

class CodeWritingCrew:
    def __init__(self, prompt: str):
        # If code_writer_agent is an instance:
        self.agent_instance = code_writer_agent
        # If CodeWriterAgent was a class, it would be: self.agent_instance = CodeWriterAgent()
        self.crew = Crew(
            name="CodeWritingCrew", # Added a name for the crew
            agents=[self.agent_instance], # Must be a list of agent instances
            tasks=[Task(agent=self.agent_instance, description=prompt, expected_output="Generated code based on the prompt.")],
            llm="gemini/gemini-1.5-flash-latest",
            verbose=True # Or as per desired default
        )
    def run(self):
        return self.crew.kickoff()
