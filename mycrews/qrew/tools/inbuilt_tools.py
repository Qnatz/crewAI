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
    FileWriterTool,
    CodeDocsSearchTool,
    GithubSearchTool,
    DirectoryReadTool,
    DirectorySearchTool,
    TXTSearchTool,
    PDFSearchTool,
    MDXSearchTool,
    EXASearchTool,
    WebsiteSearchTool,
    SerperDevTool,
    RagTool,
)
from ..tools.text_embedder_tool import TextEmbedderTool
from crewai.tools.base_tool import BaseTool  # Updated import path
from pydantic import BaseModel, Field  # Updated to use standard Pydantic v2 imports

# API Key Placeholders (using os.getenv)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# Add other API key retrievals as necessary based on tool requirements

# Basic Tool Instantiations
code_interpreter_tool = CodeInterpreterTool()
file_read_tool = FileReadTool()
file_write_tool = FileWriterTool()
directory_read_tool = DirectoryReadTool()
directory_search_tool = DirectorySearchTool()
code_docs_search_tool = CodeDocsSearchTool()

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

txt_search_tool = TXTSearchTool()
pdf_search_tool = PDFSearchTool()
mdx_search_tool = MDXSearchTool()

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

# Local Embedder for RAG
try:
    local_text_embedder = TextEmbedderTool()
    print("Local TFLite TextEmbedderTool initialized successfully.")
except Exception as e:
    local_text_embedder = None
    print(f"Warning: Failed to initialize Local TFLite TextEmbedderTool: {e}. RagTool might fall back to default or fail if it requires an embedder.")


# Custom/Placeholder Tool Definitions
class UIConverterToolPlaceholder(BaseTool):
    name: str = "UI Converter Placeholder"
    description: str = "Converts UI descriptions or designs to code. Needs real implementation."
    config: dict = {}

    def _run(self, task_details: str) -> str:
        effective_kwargs = self.config
        print(f"Placeholder: UIConverterTool running for: {task_details}, with stored config {effective_kwargs}")
        return f"Placeholder: Converted UI for task: {task_details}"

    def with_config(self, **kwargs):
        self.config = kwargs
        print(f"Placeholder: UIConverterTool instance configured with {kwargs}. Call run() on this instance.")
        return self

ui_converter = UIConverterToolPlaceholder()

class SchemaGeneratorToolPlaceholder(BaseTool):
    name: str = "Schema Generator Placeholder"
    description: str = "Generates database or API schemas from descriptions. Needs real implementation."

    def _run(self, description_and_type: str) -> str:
        print(f"Placeholder: SchemaGeneratorTool generating schema for: {description_and_type}")
        return f"Placeholder: Generated schema for {description_and_type}"

schema_generator = SchemaGeneratorToolPlaceholder()

class SecurityScannerToolPlaceholder(BaseTool):
    name: str = "Security Scanner Placeholder"
    description: str = "Scans code or configurations for vulnerabilities. Needs real implementation."

    def _run(self, path_to_scan: str) -> str:
        print(f"Placeholder: SecurityScannerTool scanning: {path_to_scan}")
        return f"Placeholder: No vulnerabilities found in {path_to_scan} (placeholder)"

security_scanner = SecurityScannerToolPlaceholder()

def ai_code_generator_func(task_description: str, framework: str):
    print(f"Placeholder: AI Code Generation for task: {task_description}, framework: {framework}")
    return f"# Placeholder code for {task_description} in {framework}\npass"

class AICodeGeneratorArgs(BaseModel):
    task_description: str = Field(..., description="Description of the coding task.")
    framework: str = Field(..., description="The framework to generate code for.")

class AICodeGeneratorToolWrapper(BaseTool):
    name: str = "AI Code Generator"
    description: str = "Generates code snippets based on task description and framework using an AI model."
    args_schema: type[BaseModel] = AICodeGeneratorArgs

    def _run(self, task_description: str, framework: str) -> str:
        return ai_code_generator_func(task_description, framework)

ai_code_generator = AICodeGeneratorToolWrapper()

# RAG Tool Configuration Function
_configured_rag_tools = {}

def configure_rag_tools(knowledge_bases: dict):
    global _configured_rag_tools
    _configured_rag_tools.clear()
    for name, path_or_config in knowledge_bases.items():
        try:
            tool_name = f"{name.replace('_', ' ').title()} RAG Search"
            tool_description = f"Performs RAG search over the {name.replace('_', ' ')} knowledge base. Config: '{path_or_config}'."
            if local_text_embedder:
                tool_instance = RagTool(
                    source=path_or_config,
                    name=tool_name,
                    description=tool_description,
                    embedder=local_text_embedder  # Attempt to pass the local embedder
                )
                print(f"Initialized RAG tool for '{name}' using source '{path_or_config}' with local TFLite embedder.")
            else:
                # Fallback to default RagTool instantiation if local_text_embedder failed
                tool_instance = RagTool(
                    source=path_or_config,
                    name=tool_name,
                    description=tool_description
                )
                print(f"Initialized RAG tool for '{name}' using source '{path_or_config}' (local embedder failed, using RagTool default behavior).")
            _configured_rag_tools[name] = tool_instance
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
cloud_dev_tools = [website_search_tool, code_docs_search_tool, github_search_tool]
mobile_dev_tools = [website_search_tool, github_search_tool, code_docs_search_tool, ui_converter]
web_dev_tools = file_system_tools + search_tools_general + code_search_tools + [ui_converter, serper_dev_tool]

security_tools = [security_scanner]
schema_tools = [schema_generator, code_docs_search_tool]
dev_utility_tools = [
    ai_code_generator,
    code_docs_search_tool,
    github_search_tool,
    code_interpreter_tool,
    file_read_tool,
    file_write_tool
]

coordinator_tools = [file_read_tool, directory_search_tool, github_search_tool, website_search_tool]
base_developer_tools = file_system_tools + [code_interpreter_tool, github_search_tool, code_docs_search_tool, ai_code_generator]

python_docs_tool = CodeDocsSearchTool(name="Python Documentation Search", description="Searches official Python documentation.")

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
