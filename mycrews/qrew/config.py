from crewai import Task
from uuid import uuid4

Task.DEFAULT_SCHEMA = {
    "id": {"type": "uuid", "default_factory": uuid4},
    "description": {"type": "string"},
    "expected_output": {"type": "string", "default": ""},
    "payload": {"type": "object", "default": {}},
    "successCriteria": {"type": "list[string]", "default": []},
    "maxRetries": {"type": "integer", "default": 2},
    "metadata": {"type": "object", "default": {}},
}
print("CrewAI Task.DEFAULT_SCHEMA configured in config.py")
