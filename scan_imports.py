import ast
import os

def find_imported_modules(directory):
    imported_modules = set()
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content, filename=file_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                # Get the base module, e.g., 'os.path' -> 'os'
                                imported_modules.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            # For 'from . import foo' or 'from ..bar import baz', node.module might be None or start with '.'
                            # We are interested in external or top-level internal modules.
                            if node.module:
                                imported_modules.add(node.module.split('.')[0])
                            # If node.module is None (e.g. from . import foo), and level > 0,
                            # it's a relative import. We can choose to ignore these or try to resolve.
                            # For this task, we are mainly interested in the first part of the module name.
                            # If node.module is None, it implies a relative import from the current package.
                            # These are not typically "external" dependencies in the usual sense.
                            # Example: from .utils import something -> module name is 'utils' if resolved,
                            # but node.module is None and level is 1.
                            # The split('.')[0] above handles cases like 'crewai.tools' -> 'crewai'
                            # For relative imports like 'from .module import name', node.module is None.
                            # We will skip these if node.module is None, as they don't represent external packages directly.
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")
    return sorted(list(imported_modules))

if __name__ == "__main__":
    # Assuming the script is run from the root of the repository or /app
    # and 'src/crewai' is the target directory.
    target_directory = "src/crewai"
    if not os.path.exists(target_directory):
        # Fallback if running from a different CWD, though tools usually run from /app
        target_directory = os.path.join(os.getcwd(), "src/crewai")
        if not os.path.exists(target_directory) and os.path.exists("crewai"): # If src/crewai not found, maybe it's just crewai
             target_directory = "crewai"


    if os.path.exists(target_directory):
        modules = find_imported_modules(target_directory)
        for module_name in modules:
            print(module_name)
    else:
        print(f"Directory not found: {target_directory}")
        print(f"Current working directory: {os.getcwd()}")
        print("Please ensure the script is run from a location where 'src/crewai' or 'crewai' is accessible.")

# To make the output cleaner for the specific request,
# filter out empty strings or '.' if they somehow get added.
# modules = [m for m in modules if m and m != '.']
# The current logic for ast.ImportFrom with `if node.module:` should prevent adding `.` from `from . import X`
# and `split('.')[0]` would prevent `.` from `from .submodule import Y` (module would be `.submodule`).
# The current logic `if node.module:` means relative imports `from . import X` are skipped.
# For `from .submodule import Y`, `node.module` is `.submodule`, so `split('.')[0]` will give an empty string.
# Let's adjust the extraction for ImportFrom to handle this.

# Revised script with better handling for ImportFrom and relative imports:

import ast
import os

def find_imported_modules_revised(directory):
    imported_modules = set()
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content, filename=file_path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imported_modules.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:  # Handles 'from package import module' or 'from package.module import name'
                                # If level > 0, it's a relative import within a package, e.g., from .sibling import X
                                # node.module would be like 'sibling' for 'from .sibling import X' if level=1
                                # or 'sub.sibling' for 'from .sub.sibling import X'
                                # For 'from external_lib.module import X', node.module is 'external_lib.module'
                                # We only want the top-level package name.
                                if node.level == 0: # Absolute import
                                    imported_modules.add(node.module.split('.')[0])
                                else: # Relative import like 'from . import foo' or 'from .bar import baz'
                                    # These are internal to the 'crewai' package structure.
                                    # We are primarily interested in external dependencies.
                                    # If you wanted to capture the first part of a relative import like '.bar',
                                    # you might do:
                                    # first_part = node.module.split('.')[0]
                                    # if first_part: imported_modules.add(first_part)
                                    # However, the goal is external dependencies, so we mostly care about level 0.
                                    pass # Ignoring relative imports for this task's focus on external deps

                except UnicodeDecodeError:
                    print(f"UnicodeDecodeError: Could not read file {file_path}. Skipping.")
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")

    # Filter out empty strings that might arise from certain relative import syntaxes if not handled carefully
    return sorted(list(m for m in imported_modules if m))

if __name__ == "__main__":
    target_directory = "src/crewai"
    # In the tool environment, the CWD is /app
    if not os.path.isdir(target_directory):
        print(f"Directory '{target_directory}' not found in CWD '{os.getcwd()}'. Trying 'crewai'.")
        target_directory = "crewai" # Try this if src/crewai doesn't exist (e.g. if repo root is different)

    if os.path.isdir(target_directory):
        modules = find_imported_modules_revised(target_directory)
        for module_name in modules:
            print(module_name)
    else:
        print(f"Target directory '{target_directory}' not found. Searched in '{os.getcwd()}'.")
        # Listing directory contents for debugging in case the path is wrong
        print("Contents of current directory:")
        for item in os.listdir("."):
            print(item)
        if os.path.exists("src"):
            print("Contents of 'src' directory:")
            for item in os.listdir("src"):
                 print(item)
