from crewai import Crew, Task
from q_ware.orchestrators.final_assembler_agent.agent import final_assembler_agent # Assuming instance export

# final_assembler_agent is an instance. We need to ensure it's used correctly.
# If final_assembler_agent is an instance:
# agent_instance = final_assembler_agent
# If it was a class FinalAssemblerAgent, it would be: agent_instance = FinalAssemblerAgent()

class FinalAssemblyCrew:
    def __init__(self, assembly_instructions: str): # Or other relevant input
        self.agent_instance = final_assembler_agent
        self.crew = Crew(
            name="FinalAssemblyCrew",
            agents=[self.agent_instance],
            tasks=[Task(agent=self.agent_instance, description=assembly_instructions, expected_output="Successfully assembled and packaged solution.")],
            llm="gemini/gemini-1.5-flash-latest",
            verbose=True
        )
    def run(self):
        return self.crew.kickoff()
