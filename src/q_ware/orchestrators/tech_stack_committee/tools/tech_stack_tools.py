from crewai.tools import BaseTool

class TechResearchTool(BaseTool):
    name: str = "Tech Research Tool" # Explicitly defining name as per BaseTool requirements
    description: str = "Helps research and compare technologies based on industry trends and benchmarks."

    def _run(self, query: str) -> str: # query should be typed as str
        # You can replace this with LangChain web search or local embeddings later
        return f"TechResearchTool result for: {query}"
