from crewai_tools import BaseTool
import os

class FileReadTool(BaseTool):
    name: str = "File Read Tool"
    description: str = "Reads the content of a specified file. Input must be the file path."

    def _run(self, file_path: str) -> str:
        try:
            # Security check: Ensure the path is within an allowed directory if necessary.
            # For now, assuming paths are relative to a project root or otherwise controlled.
            # Example: if not file_path.startswith("/app/data/"): return "Error: Access denied."

            # Ensure the path is not absolute or trying to escape a sandbox (conceptual)
            if os.path.isabs(file_path) or ".." in file_path:
                return "Error: Invalid file path. Only relative paths within the project are allowed."

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return f"Error: File not found at path: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

class FileWriteTool(BaseTool):
    name: str = "File Write Tool"
    description: str = "Writes content to a specified file. Input must be a dictionary with 'file_path' and 'content'."

    def _run(self, **kwargs) -> str: # Using kwargs to expect 'file_path' and 'content'
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")

        if not file_path or content is None: # content can be empty string, so check for None
            return "Error: 'file_path' and 'content' must be provided."

        try:
            # Security check: Ensure the path is within an allowed directory.
            if os.path.isabs(file_path) or ".." in file_path:
                return "Error: Invalid file path. Only relative paths within the project are allowed."

            # Create directories if they don't exist
            # Ensure the directory part of the path is not empty before trying to create it
            dir_name = os.path.dirname(file_path)
            if dir_name: # Only call makedirs if there's a directory part
                os.makedirs(dir_name, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to file: {file_path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"
