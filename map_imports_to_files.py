import ast
import os
import json
from collections import defaultdict

# Define dependencies based on previous analysis
# 1. Core dependencies from pyproject.toml (excluding 'uv')
# PyPI names
core_dependencies_pypi = [
    'appdirs', 'auth0-python', 'blinker', 'chromadb', 'click', 'instructor',
    'json-repair', 'json5', 'jsonref', 'litellm', 'onnxruntime', 'openai',
    'opentelemetry-api', 'opentelemetry-exporter-otlp-proto-http',
    'opentelemetry-sdk', 'openpyxl', 'pdfplumber', 'pydantic', 'python-dotenv',
    'pyvis', 'regex', 'tokenizers', 'tomli', 'tomli-w'
]

# 2. Optional dependencies from pyproject.toml
# PyPI names
optional_dependencies_pypi = {
    'agentops': ['agentops'],
    'aisuite': ['aisuite'],
    'docling': ['docling'],
    'embeddings': ['tiktoken'],
    'mem0': ['mem0ai'],
    'openpyxl_opt': ['openpyxl'], # Renamed key to avoid clash if needed, value is PyPI name
    'pandas_opt': ['pandas'],   # Renamed key to avoid clash, value is PyPI name
    'pdfplumber_opt': ['pdfplumber'], # Renamed key to avoid clash, value is PyPI name
    'tools': ['crewai-tools']
}

# 3. Additionally imported modules (discovered from AST scan)
# These are already import names
additionally_imported_modules_import_names = [
    'cryptography', 'ibm_watsonx_ai', 'langchain_core', 'langgraph',
    'numpy', 'packaging', 'requests', 'rich', 'yaml'
]

# Mapping from PyPI name to actual import name(s)
# This is crucial for matching.
pypi_to_import_name_map = {
    "appdirs": "appdirs",
    "auth0-python": "auth0",
    "blinker": "blinker",
    "chromadb": "chromadb",
    "click": "click",
    "instructor": "instructor",
    "json-repair": "json_repair",
    "json5": "json5",
    "jsonref": "jsonref",
    "litellm": "litellm",
    "onnxruntime": "onnxruntime",
    "openai": "openai",
    "opentelemetry-api": "opentelemetry",
    "opentelemetry-exporter-otlp-proto-http": "opentelemetry",
    "opentelemetry-sdk": "opentelemetry",
    "openpyxl": "openpyxl",
    "pdfplumber": "pdfplumber",
    "pydantic": "pydantic", # also pydantic_core, but we map to pydantic
    "python-dotenv": "dotenv",
    "pyvis": "pyvis",
    "regex": "regex",
    "tokenizers": "tokenizers",
    "tomli": "tomli",
    "tomli-w": "tomli_w",
    "agentops": "agentops", # from optional
    "aisuite": "aisuite",   # from optional
    "docling": "docling",   # from optional
    "tiktoken": "tiktoken", # from optional
    "mem0ai": "mem0",       # from optional
    "pandas": "pandas",     # from optional
    "crewai-tools": "crewai_tools" # from optional
    # The additionally_imported_modules_import_names are already import names
}

# Create a flat list of all target *import names* to look for
target_import_names = set()

# Add core dependency import names
for pypi_name in core_dependencies_pypi:
    if pypi_name in pypi_to_import_name_map:
        target_import_names.add(pypi_to_import_name_map[pypi_name])
    else:
        target_import_names.add(pypi_name.replace("-", "_")) # Default normalization

# Add optional dependency import names
for pypi_list in optional_dependencies_pypi.values():
    for pypi_name in pypi_list:
        if pypi_name in pypi_to_import_name_map:
            target_import_names.add(pypi_to_import_name_map[pypi_name])
        else:
            target_import_names.add(pypi_name.replace("-", "_"))

# Add additionally imported module names
for import_name in additionally_imported_modules_import_names:
    target_import_names.add(import_name)

# The dependency map will store import_name -> list of files
dependency_map = defaultdict(set) # Use set to avoid duplicate file paths per module

def map_imports(directory, target_imports, file_map):
    for root, _, files in os.walk(directory):
        # Skip template directories that caused issues before
        if "cli/templates" in root:
            continue
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content, filename=file_path)
                    for node in ast.walk(tree):
                        imported_module_base = None
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imported_module_base = alias.name.split('.')[0]
                                if imported_module_base in target_imports:
                                    file_map[imported_module_base].add(file_path)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module: # e.g., 'from package.module import ...' or 'from package import ...'
                                # node.level == 0 means absolute import, e.g. 'from foo import bar'
                                # node.level > 0 means relative import, e.g. 'from . import foo'
                                if node.level == 0: # Only consider absolute imports for external deps
                                    imported_module_base = node.module.split('.')[0]
                                    if imported_module_base in target_imports:
                                        file_map[imported_module_base].add(file_path)
                            # For 'from . import X' or 'from .sub import Y', node.module is None or starts with '.'
                            # These are relative imports, not what we're tracking for external dependencies.
                except UnicodeDecodeError:
                    print(f"UnicodeDecodeError: Could not read file {file_path}. Skipping.")
                except Exception as e:
                    # This will catch ast.parse errors for files with template syntax too
                    print(f"Error parsing {file_path}: {e}")
    return file_map

if __name__ == "__main__":
    target_directory = "src/crewai"
    if not os.path.isdir(target_directory):
        print(f"Directory '{target_directory}' not found in CWD '{os.getcwd()}'. Trying 'crewai'.")
        target_directory = "crewai"

    if os.path.isdir(target_directory):
        dependency_map_results = map_imports(target_directory, target_import_names, dependency_map)

        # Convert sets to lists for JSON serialization
        output_map = {k: sorted(list(v)) for k, v in dependency_map_results.items()}

        print(json.dumps(output_map, indent=2))
    else:
        print(f"Target directory '{target_directory}' not found. Searched in '{os.getcwd()}'.")
