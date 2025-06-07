from crewai_tools import tool

@tool
def placeholder_offline_sync_tool(param: str) -> str:
    """Placeholder tool for offline/local-first SyncAgent. Simulates data reconciliation when reconnecting."""
    return "Offline SyncAgent tool executed with " + param

my_tools = [placeholder_offline_sync_tool]
