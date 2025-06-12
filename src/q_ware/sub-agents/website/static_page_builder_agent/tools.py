from crewai.tools import tool

@tool
def placeholder_tool(param: str) -> str:
    """Placeholder tool for StaticPageBuilderAgent."""
    return "Tool executed with " + param

my_tools = [placeholder_tool]
