# mycrews/qrew/tools/inbuilt_tools.py
# Description: Defines and groups a suite of tools for use by CrewAI agents.
# Notes:
# - Ensure API keys (SERPER_API_KEY, EXA_API_KEY, GITHUB_TOKEN) are set as environment variables.
# - Placeholder tools (UIConverter, SchemaGenerator, SecurityScanner) need real implementations.
# - RAG tool configuration is a placeholder and depends on the specific RagTool API.

import os
from crewai_tools import (
    CodeInterpreterTool,
    FileReadTool,
    FileWriterTool, # Changed FileWriteTool to FileWriterTool
    CodeDocsSearchTool,
    GithubSearchTool,
    DirectoryReadTool,
    DirectorySearchTool,
    TXTSearchTool, # Assuming this was meant if used, else remove. Previous plan did not list specific text search tools in groups.
    PDFSearchTool,   # Assuming this was meant if used, else remove.
    MDXSearchTool,   # Assuming this was meant if used, else remove.
    EXASearchTool, # Changed ExaSearchTool to EXASearchTool
    WebsiteSearchTool,
    SerperDevTool,
    RagTool  # Added RagTool
)

# API Key Placeholders (using os.getenv)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Add other API key retrievals as necessary based on tool requirements

# Basic Tool Instantiations
# Note: safe_mode=True for CodeInterpreterTool is a custom addition not in standard crewai_tools
# For crewai_tools.CodeInterpreterTool, it does not take safe_mode or timeout.
# We will assume it's a custom version or this parameter will be ignored if using stock.
# For now, instantiating as per crewai_tools standard.
code_interpreter_tool = CodeInterpreterTool() # Standard instantiation
file_read_tool = FileReadTool()
file_write_tool = FileWriterTool() # Changed FileWriteTool to FileWriterTool
directory_read_tool = DirectoryReadTool()
directory_search_tool = DirectorySearchTool()
code_docs_search_tool = CodeDocsSearchTool() # Standard, specific docs can be set via source property or method if available

# Robust initialization for GithubSearchTool
if GITHUB_TOKEN:
    try:
        github_search_tool = GithubSearchTool(gh_token=GITHUB_TOKEN, content_types=['code', 'repo', 'issue'])
        print("GithubSearchTool initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to initialize GithubSearchTool (Token was present but init failed): {e}. Tool will be disabled.")
        github_search_tool = None
else:
    print("Warning: GITHUB_TOKEN not found in environment. GithubSearchTool will be disabled.")
    github_search_tool = None

txt_search_tool = TXTSearchTool() # If this specific tool exists and is used
pdf_search_tool = PDFSearchTool() # If this specific tool exists and is used
mdx_search_tool = MDXSearchTool() # If this specific tool exists and is used

# Robust initialization for EXASearchTool
if EXA_API_KEY:
    try:
        exa_search_tool = EXASearchTool(api_key=EXA_API_KEY)
        print("EXASearchTool initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to initialize EXASearchTool (API key was present but init failed): {e}. Tool will be disabled.")
        exa_search_tool = None
else:
    print("Warning: EXA_API_KEY not found in environment. EXASearchTool will be disabled.")
    exa_search_tool = None

# Robust initialization for SerperDevTool
if SERPER_API_KEY:
    try:
        serper_dev_tool = SerperDevTool(api_key=SERPER_API_KEY)
        print("SerperDevTool initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to initialize SerperDevTool (API key was present but init failed): {e}. Tool will be disabled.")
        serper_dev_tool = None
else:
    print("Warning: SERPER_API_KEY not found in environment. SerperDevTool will be disabled.")
    serper_dev_tool = None

website_search_tool = WebsiteSearchTool()


# Custom/Placeholder Tool Definitions
class UIConverterToolPlaceholder:
    def __init__(self):
        self.name = "UI Converter Placeholder"
        self.description = "Converts UI descriptions or designs to code. Needs real implementation."
        self.config = {} # To store any config from with_config

    def run(self, task_details: str, **kwargs): # Made 'run' more generic
        # task_details might be a string like "Convert login screen mock_up.png to Android XML"
        effective_kwargs = {**self.config, **kwargs} # Combine instance and runtime kwargs
        print(f"Placeholder: UIConverterTool running for: {task_details}, with config {effective_kwargs}")
        return f"Placeholder: Converted UI for task: {task_details}"

    def with_config(self, **kwargs):
        # This allows specialized versions, returning a new instance or configured self
        print(f"Placeholder: UIConverterTool configured with {kwargs}. Returning self for chaining.")
        # In a real scenario, you might store kwargs or return a new configured instance.
        self.config = kwargs
        return self

ui_converter = UIConverterToolPlaceholder()

class SchemaGeneratorToolPlaceholder:
    def __init__(self):
        self.name = "Schema Generator Placeholder"
        self.description = "Generates database or API schemas from descriptions. Needs real implementation."

    def run(self, description: str, type: str = "database", **kwargs):
        print(f"Placeholder: SchemaGeneratorTool generating {type} schema for: {description}, extras: {kwargs}")
        return f"Placeholder: Generated {type} schema for {description}"

schema_generator = SchemaGeneratorToolPlaceholder()

class SecurityScannerToolPlaceholder:
    def __init__(self):
        self.name = "Security Scanner Placeholder"
        self.description = "Scans code or configurations for vulnerabilities. Needs real implementation."

    def run(self, path_to_scan: str, **kwargs):
        print(f"Placeholder: SecurityScannerTool scanning: {path_to_scan}, config: {kwargs}")
        return f"Placeholder: No vulnerabilities found in {path_to_scan} (placeholder)"

security_scanner = SecurityScannerToolPlaceholder()

def ai_code_generator_func(task_description: str, framework: str):
    # Connect to your preferred AI service:
    # Option 1: Local LLM (LM Studio, Ollama)
    # Option 2: Cloud API (OpenAI, Anthropic, Mistral)
    # Option 3: HuggingFace endpoint
    print(f"Placeholder: AI Code Generation for task: {task_description}, framework: {framework}")
    return f"# Placeholder code for {task_description} in {framework}\npass"

class AICodeGeneratorToolWrapper:
    def __init__(self, func_to_wrap):
        self.name = "AI Code Generator"
        self.description = "Generates code snippets based on task description and framework using an AI model."
        self.func = func_to_wrap
        # Make it usable as a crewai_tool (duck typing)
        self.agent = None
        self.crew = None

    def run(self, task_description: str, framework: str, **kwargs): # Make it flexible
            return self.func(task_description, framework)

ai_code_generator = AICodeGeneratorToolWrapper(ai_code_generator_func)

# RAG Tool Configuration Function
_configured_rag_tools = {}

def configure_rag_tools(knowledge_bases: dict):
    global _configured_rag_tools
    _configured_rag_tools.clear() # Clear previous configurations
    for name, path_or_config in knowledge_bases.items():
        try:
            tool_name = f"{name.replace('_', ' ').title()} RAG Search"
            tool_description = f"Performs RAG search over the {name.replace('_', ' ')} knowledge base. Config: '{path_or_config}'."

            # Assuming RagTool might take the direct path/config at init or needs a specific method later
            # For now, this is a generic RagTool from crewai_tools
            # If it needs specific setup like vectorstore path or db_connection:
            # tool_instance = RagTool(config=path_or_config, name=tool_name, description=tool_description)
            # Or if it has a load method:
            # tool_instance = RagTool(name=tool_name, description=tool_description)
            # tool_instance.load_data(path_or_config) # Fictional method

            # Based on crewai_tools.RagTool, it often takes a `knowledge_base` argument or similar
            # For this placeholder, we'll assume it can be instantiated and then configured if needed,
            # or that the path_or_config is a direct source it can use.
            # Let's assume `path_or_config` is a string representing a file path or directory for the KB.
            tool_instance = RagTool(source=path_or_config, name=tool_name, description=tool_description)

            _configured_rag_tools[name] = tool_instance
            print(f"Initialized RAG tool for '{name}' using source '{path_or_config}'.")
        except Exception as e:
            print(f"Failed to initialize RAG tool for '{name}' with '{path_or_config}': {e}")
    return _configured_rag_tools

def get_rag_tool(name: str):
    return _configured_rag_tools.get(name)

# Preconfigured Tool Groups
file_system_tools = [file_read_tool, file_write_tool, directory_read_tool, directory_search_tool]
search_tools_general = [serper_dev_tool, exa_search_tool, website_search_tool]
code_search_tools = [code_docs_search_tool, github_search_tool]

api_dev_tools = [website_search_tool, code_docs_search_tool, exa_search_tool, github_search_tool, schema_generator]
cloud_dev_tools = [website_search_tool, code_docs_search_tool, github_search_tool] # Keep as is for now
mobile_dev_tools = [website_search_tool, github_search_tool, code_docs_search_tool, ui_converter]
web_dev_tools = file_system_tools + search_tools_general + code_search_tools + [ui_converter, serper_dev_tool]

security_tools = [security_scanner]
schema_tools = [schema_generator, code_docs_search_tool]
dev_utility_tools = [
    ai_code_generator,
    code_docs_search_tool,
    github_search_tool,
    code_interpreter_tool,
    file_read_tool, # Explicitly file_read_tool
    file_write_tool # Explicitly file_write_tool
]

coordinator_tools = [file_read_tool, directory_search_tool, github_search_tool, website_search_tool]
base_developer_tools = file_system_tools + [code_interpreter_tool, github_search_tool, code_docs_search_tool, ai_code_generator]

# Example: For Python docs - can be configured after instantiation or by creating specific instances
# If CodeDocsSearchTool can be configured for a specific source:
# python_docs_tool = CodeDocsSearchTool(docs_url='https://docs.python.org/3/', name="Python Documentation Search", description="Searches official Python documentation.")
# For now, using the generic one and assuming it can search various sources or needs to be configured at runtime.
python_docs_tool = CodeDocsSearchTool(name="Python Documentation Search", description="Searches official Python documentation.")
# react_docs_tool = CodeDocsSearchTool(name="React Documentation Search", description="Searches official React documentation.")
# Similar for other framework_docs_tools

# All tools defined or wrapped here aim for pure Python dependencies for Termux compatibility.
# (With the understanding that underlying OS calls for file system access are standard)
# The actual execution of tools like CodeInterpreterTool might have its own sandboxing needs.
# Network tools (Exa, Serper, Website, Github) require internet access.
# Placeholder tools are by definition pure Python.
# RagTool's dependencies would need to be Termux-compatible if used there.

print("QREW In-built tools module loaded.")
if SERPER_API_KEY:
    print("Serper API Key: Loaded")
else:
    print("Warning: Serper API Key (SERPER_API_KEY) not found in environment.")

if EXA_API_KEY:
    print("Exa API Key: Loaded")
else:
    print("Warning: Exa API Key (EXA_API_KEY) not found in environment.")

if GITHUB_TOKEN:
    print("GitHub Token: Loaded")
else:
    print("Warning: GitHub Token (GITHUB_TOKEN) for GithubSearchTool not found in environment. Some functionalities might be limited or fail.")

# Test RAG configuration (example)
# sample_kbs = {
# "project_docs": "./project_specific_docs",
# "api_standards": "./company_api_standards.md"
# }
# configure_rag_tools(sample_kbs)
# print(f"Configured RAG tools: {_configured_rag_tools}")

# Note: Specific text search tools (TXTSearchTool, PDFSearchTool, MDXSearchTool) were imported
# but not explicitly added to any default groups. They can be added as needed or used directly.
# Their utility often overlaps with RagTool or WebsiteSearchTool (for local HTML/Text files).
# For example, pdf_search_tool can be added to file_system_tools if local PDF search is common.
# file_system_tools.append(pdf_search_tool) # Example
#
# Also, CodeInterpreterTool does not have `safe_mode` or `timeout` parameters in its standard constructor.
# These were removed from the instantiation. If custom behavior is needed, the tool might need to be subclassed or configured differently.
