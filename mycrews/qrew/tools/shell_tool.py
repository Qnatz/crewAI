import subprocess
from crewai.tools.base_tool import tool

@tool("Shell Tool")
def shell_tool(command: str) -> str:
    """Executes a shell command and returns the result with stdout and stderr."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            return f"Command executed successfully:\nOutput:\n{stdout}"
        else:
            return f"Command failed with error code {process.returncode}:\nError:\n{stderr}\nOutput:\n{stdout}"
    except Exception as e:
        return f"An error occurred while executing the command: {e}"
