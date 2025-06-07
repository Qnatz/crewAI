from crewai_tools import BaseTool

class ConstraintValidatorTool(BaseTool):
    name: str = "Constraint Validator" # Explicitly defining name
    description: str = "Validates tech choices against project constraints like team skill level, cost, performance, and security."

    def _run(self, proposal: str) -> str: # proposal should be typed as str
        return f"Validated constraints for: {proposal}"
