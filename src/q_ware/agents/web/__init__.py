# This file makes 'web' a package.
from .agent import web_project_coordinator_agent # Added coordinator
from .static_page_builder_agent import static_page_builder_agent
from .dynamic_page_builder_agent import dynamic_page_builder_agent
from .asset_manager_agent import asset_manager_agent

__all__ = [
    "web_project_coordinator_agent", # Added coordinator
    "static_page_builder_agent",
    "dynamic_page_builder_agent",
    "asset_manager_agent"
]
