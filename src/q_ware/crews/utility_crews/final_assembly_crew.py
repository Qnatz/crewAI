from crewai import Crew, Task
from q_ware.orchestrators.final_assembler_agent.agent import final_assembler_agent # Assuming instance export

# final_assembler_agent is an instance. We need to ensure it's used correctly.
# If final_assembler_agent is an instance:
# agent_instance = final_assembler_agent
# If it was a class FinalAssemblerAgent, it would be: agent_instance = FinalAssemblerAgent()
from q_ware.llm_config import get_llm

class FinalAssemblyCrew:
    def __init__(self, assembly_instructions: str): # Or other relevant input
        self.agent_instance = final_assembler_agent
        llm = get_llm()
        self.crew = Crew(
            name="FinalAssemblyCrew",
            agents=[self.agent_instance],
            tasks=[Task(agent=self.agent_instance, description=assembly_instructions, expected_output="Successfully assembled and packaged solution.")],
            llm=llm,
            verbose=True
        )
    def run(self):
        return self.crew.kickoff()
