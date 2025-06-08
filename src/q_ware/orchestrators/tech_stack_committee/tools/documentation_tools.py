from crewai.tools import BaseTool

class MarkdownWriterTool(BaseTool):
    name: str = "Markdown Writer" # Explicitly defining name
    description: str = "Formats finalized decisions and explanations into Markdown syntax for documentation."

    def _run(self, stack_info: str) -> str: # stack_info should be typed as str
        return f"Formatted TECH_STACK.md for: {stack_info}"
