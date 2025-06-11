from crewai import Task
from uuid import uuid4

Task.DEFAULT_SCHEMA = {
    "id": {"type": "uuid", "default_factory": uuid4},
    "description": {"type": "string"},
    "expected_output": {"type": "string", "default": ""},
    "successCriteria": {"type": "list[string]", "default": []},
    "maxRetries": {"type": "integer", "default": 2},
    "metadata": {"type": "object", "default": {}},
}
print("CrewAI Task.DEFAULT_SCHEMA configured in config.py")

def example_summary_validator(task: Task, result: dict) -> bool:
    description_lower = task.description.lower()
    if "summary" in description_lower or "summarize" in description_lower:
        if not isinstance(result, dict) or "summary" not in result or not result.get("summary"):
            print(f"QualityGate Fail (Custom Validator): Task '{task.description}' expected a summary, but it was missing or empty in the result.")
            return False
    return True
