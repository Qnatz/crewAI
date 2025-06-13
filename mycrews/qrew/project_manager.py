# mycrews/qrew/project_manager.py
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from .utils import ErrorSummary

class ProjectStateManager:
    def __init__(self, project_name: str):
        self.project_info = self.get_or_create_project(project_name)
        self.state_file = Path(self.project_info['path']) / "state.json"
        self.error_summary = ErrorSummary()
        self.load_state()

    def _slugify(self, name: str) -> str:
        safe = "".join(c if c.isalnum() else "_" for c in name).lower()
        return safe[:50]

    def get_or_create_project(self, name: str) -> dict:
        projects_index_file = Path(__file__).parent / "projects_index.json"
        projects_root_dir = Path(__file__).parent / "projects/"

        index = {}
        if projects_index_file.exists():
            try:
                index = json.loads(projects_index_file.read_text())
            except json.JSONDecodeError:
                index = {} # Handle empty or corrupted file

        name_hash = hashlib.sha1(name.encode()).hexdigest()[:8]
        project_id = f"{self._slugify(name)}_{name_hash}"

        if project_id in index:
            project_info = index[project_id]
            # Ensure path is absolute for internal use, even if stored relative
            project_info["path"] = str(projects_root_dir / project_id)
        else:
            projects_root_dir.mkdir(parents=True, exist_ok=True)
            project_path = projects_root_dir / project_id
            project_path.mkdir(parents=True, exist_ok=True)

            project_info = {
                "name": name,
                "id": project_id,
                "path": str(project_path) # Store as string
            }
            index[project_id] = {"name": name, "id": project_id, "path": str(project_path)} # Storing path relative to root for index
            projects_index_file.write_text(json.dumps(index, indent=2))

        return project_info

    def load_state(self):
        if self.state_file.exists():
            try:
                self.state = json.loads(self.state_file.read_text())
                # Rehydrate error_summary
                for record in self.state.get("error_summary", []):
                    self.error_summary.add(record["stage"], record["success"], record["message"])
            except json.JSONDecodeError:
                self.state = self._initial_state()
        else:
            self.state = self._initial_state()

    def _initial_state(self) -> dict:
        return {
            "project_name": self.project_info["name"],
            "project_id": self.project_info["id"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "current_stage": None,
            "completed_stages": [],
            "artifacts": {},
            "error_summary": [], # Will be populated by ErrorSummary object
            "status": "pending" # Possible statuses: pending, running, completed, failed
        }

    def save_state(self):
        self.state["error_summary"] = self.error_summary.to_dict()
        self.state["updated_at"] = datetime.utcnow().isoformat()
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def start_stage(self, stage_name: str):
        self.state["current_stage"] = stage_name
        self.state["status"] = "running"
        self.error_summary.add(stage_name, True, "Stage started") # Mark as success initially
        self.save_state()

    def complete_stage(self, stage_name: str, artifacts: dict = None):
        if stage_name not in self.state["completed_stages"]:
            self.state["completed_stages"].append(stage_name)
        if artifacts:
            if stage_name not in self.state["artifacts"]:
                self.state["artifacts"][stage_name] = {}
            self.state["artifacts"][stage_name].update(artifacts)

        # Add a new log entry for completion, do not modify existing ones.
        self.error_summary.add(stage_name, True, "Completed successfully")

        self.state["current_stage"] = None
        self.save_state()

    def fail_stage(self, stage_name: str, error_message: str):
        self.state["status"] = "failed"

        # Add a new log entry for failure, do not modify existing ones.
        self.error_summary.add(stage_name, False, error_message)

        self.save_state()

    def get_artifacts(self, stage_name: str = None):
        if stage_name:
            return self.state["artifacts"].get(stage_name)
        return self.state["artifacts"]

    def is_completed(self, stage_name: str) -> bool:
        return stage_name in self.state["completed_stages"]

    def resume_point(self) -> str | None:
        if self.state.get("status") == "completed":
            return None

        # This workflow can be made dynamic later if needed
        workflow_stages = ["taskmaster", "architecture", "crew_assignment", "subagent_execution", "final_assembly"]

        for stage in workflow_stages:
            if not self.is_completed(stage):
                return stage

        # If all stages are somehow completed but project isn't marked 'completed'
        # or if workflow_stages is empty.
        return workflow_stages[0] if workflow_stages else None


    def finalize_project(self):
        self.state["status"] = "completed"
        self.state["completed_at"] = datetime.utcnow().isoformat()
        self.state["current_stage"] = None
        # Add a summary completion message
        self.error_summary.add("Project", True, "Project completed successfully.")
        self.save_state()

    def get_summary(self):
        return self.error_summary
