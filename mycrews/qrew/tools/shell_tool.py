import subprocess
from crewai_tools import BaseTool

class ShellTool(BaseTool):
    name: str = "Shell Tool"
    description: str = "Executes a shell command and returns the output."

    def _run(self, command: str) -> str:
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
