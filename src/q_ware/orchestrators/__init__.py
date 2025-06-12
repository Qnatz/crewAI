# This file makes 'orchestrators' a package.
# It will later export the various orchestrator agents.
from .idea_interpreter_agent import idea_interpreter_agent
from .project_architect_agent import project_architect_agent
from . import tech_stack_committee # Import the new package
from .execution_manager_agent import ExecutionManagerCrew # Or import the module: from . import execution_manager_agent
from .final_assembler_agent import final_assembler_agent # Added

__all__ = [
    "idea_interpreter_agent",
    "project_architect_agent",
    "tech_stack_committee",
    "ExecutionManagerCrew", # Or "execution_manager_agent"
    "final_assembler_agent" # Added
]
