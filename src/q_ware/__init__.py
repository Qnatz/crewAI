# Q-Ware Package Root

# Export key components for easier access
from .project_crew_factory import create_project_orchestrator
from .taskmaster.taskmaster_agent import TaskmasterAgent # Also exporting Taskmaster directly for convenience if needed

# Exporting main agent/crew categories as modules can also be useful
from . import agents
from . import orchestrators
from . import crews
from . import tools

__all__ = [
    "create_project_orchestrator",
    "TaskmasterAgent", # Added TaskmasterAgent
    "agents",
    "orchestrators",
    "crews",
    "tools"
]
