# mycrews/qrew/tools/tool_registry.py
from crewai_tools import (
    FileReadTool,
    DirectorySearchTool,
    WebsiteSearchTool,
    CodeDocsSearchTool,
)
# Assuming inbuilt_tools.py is in the same directory or accessible via .
from .inbuilt_tools import (
    SchemaGeneratorToolPlaceholder,
    # ui_converter, # Example, not in the issue's list but shows how to add more
    # security_scanner, # Example
    # ai_code_generator, # Example
)
from .github_tool_wrapper import GithubSearchWrapperTool

# The issue specifies these exact names as keys.
TOOL_REGISTRY = {
    "Read a file's content": FileReadTool(),
    "Search a directory's content": DirectorySearchTool(),
    "GitHub Search": GithubSearchWrapperTool(),
    "Search in a specific website": WebsiteSearchTool(),
    "Search a Code Docs content": CodeDocsSearchTool(),
    "Schema Generator Placeholder": SchemaGeneratorToolPlaceholder(),
    # Add more tools here as needed, for example:
    # "UI Converter": ui_converter,
    # "Security Scanner": security_scanner,
    # "AI Code Generator": ai_code_generator,
}

# Example of how to access a tool:
# file_reader = TOOL_REGISTRY.get("Read a file's content")
# if file_reader:
#     # result = file_reader.run(...)
#     pass

print("QREW Tool Registry initialized.")
