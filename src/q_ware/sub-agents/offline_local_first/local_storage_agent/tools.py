from crewai.tools import tool

@tool
def placeholder_local_storage_tool(param: str) -> str:
    """Placeholder tool for LocalStorageAgent. Simulates interaction with local DB (IndexedDB, SQLite)."""
    return "LocalStorageAgent tool executed with " + param

my_tools = [placeholder_local_storage_tool]
