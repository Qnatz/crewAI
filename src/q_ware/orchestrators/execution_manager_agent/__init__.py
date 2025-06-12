# Export the crew for easy access
from .crews.execution_manager_crew import ExecutionManagerCrew

# If there was an agent defined for execution_manager_agent itself, it would be exported here too.
# For now, focusing on making the crew available.

__all__ = [
    "ExecutionManagerCrew"
]
