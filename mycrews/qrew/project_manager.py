import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from .utils import ErrorSummary

PROJECTS_INDEX = Path(__file__).parent / "projects_index.json"
PROJECTS_ROOT = Path(__file__).parent / "projects/"

class ProjectStateManager:
    def __init__(self, project_name):
        PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
        self.project_info = self._get_or_create_project(project_name)
        self.state_file = Path(self.project_info['path']) / "state.json"
        self.error_summary = ErrorSummary()
        self.load_state()

    def _slugify(self, name: str) -> str:
        safe = "".join(c if c.isalnum() else "_" for c in name).lower()
        return safe[:50]

    def _load_index(self):
        if PROJECTS_INDEX.exists():
            try:
                return json.loads(PROJECTS_INDEX.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_index(self, index):
        PROJECTS_INDEX.write_text(json.dumps(index, indent=2))

    def _get_or_create_project(self, name: str) -> dict:
        index = self._load_index()
        name_hash = hashlib.sha1(name.encode()).hexdigest()[:8]
        key = f"{self._slugify(name)}_{name_hash}"

        if key in index:
            proj_details = index[key]
            # Assumes path stored is absolute or correctly resolvable
            proj_path = Path(proj_details["path"])
            status = "continuing"
        else:
            proj_path = PROJECTS_ROOT / key
            proj_path.mkdir(parents=True, exist_ok=True)
            proj_details = {"name": name, "id": key, "path": str(proj_path.resolve())}
            index[key] = proj_details
            self._save_index(index)
            status = "new"
        return {"status": status, **proj_details}

    def load_state(self):
        if self.state_file.exists():
            try:
                loaded_state = json.loads(self.state_file.read_text())
                self.state = loaded_state
                # When loading state, rehydrate ErrorSummary from the loaded records
                self.error_summary.records = []
                for record in self.state.get("error_summary", []):
                    # Ensure all components of the record are passed to add
                    self.error_summary.add(record["stage"], record["success"], record["message"])
            except json.JSONDecodeError:
                self.state = self._initial_state()
        else:
            self.state = self._initial_state()

    def _initial_state(self):
        return {
            "project_name": self.project_info["name"],
            "created_at": datetime.utcnow().isoformat(),
            "current_stage": "initialized",
            "completed_stages": [],
            "artifacts": {},
            "error_summary": [], # Initial error summary is empty
            "status": "in_progress"
        }

    def save_state(self):
        """Save current state to file"""
        self.state["error_summary"] = self.error_summary.to_dict()
        self.state["updated_at"] = datetime.utcnow().isoformat()

        # Ensure the directory for the state file exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True) # Added line

        self.state_file.write_text(json.dumps(self.state, indent=2))

    def start_stage(self, stage_name):
        self.state["current_stage"] = stage_name
        # No direct error_summary.add here; stage start is not an event for summary
        self.save_state()

    def complete_stage(self, stage_name, artifacts=None):
        if stage_name not in self.state["completed_stages"]:
            self.state["completed_stages"].append(stage_name)

        if artifacts:
            try:
                # Attempt to serialize to ensure artifacts are storable
                json.dumps(artifacts)
                self.state["artifacts"][stage_name] = artifacts
            except TypeError as e:
                # Log non-serializable artifacts issue
                error_msg = f"Artifacts for stage {stage_name} are not JSON serializable: {e}"
                print(f"Warning: {error_msg}")
                self.state["artifacts"][stage_name] = {"error": "not_serializable", "details": str(artifacts)}
                # Optionally, log this as a non-critical error/warning in summary
                # self.error_summary.add(stage_name, True, f"Completed with non-serializable artifacts: {error_msg}")

        self.error_summary.add(stage_name, True, "Completed successfully")
        self.save_state()

    def fail_stage(self, stage_name, error_message):
        self.state["status"] = "failed" # Mark project status as failed
        self.error_summary.add(stage_name, False, error_message)
        self.save_state()

    def get_artifacts(self, stage_name=None):
        if stage_name:
            return self.state["artifacts"].get(stage_name, {})
        return self.state["artifacts"]

    def is_completed(self, stage_name):
        return stage_name in self.state["completed_stages"]

    def resume_point(self):
        # If project is marked completed, no resume point.
        if self.state.get("status") == "completed":
            return None

        workflow_stages = [
            "taskmaster",
            "architecture",
            "crew_assignment",
            "subagent_execution",
            "final_assembly"
        ]

        for stage in workflow_stages:
            if not self.is_completed(stage):
                return stage # Return the first incomplete stage

        # If all defined workflow stages are complete, but project not finalized.
        # This could mean it's ready for finalization or an edge case.
        # For now, if all stages are done, we can consider it None (no next stage).
        # Or, it might imply a final "project_finalization" stage if it's part of the workflow.
        if all(self.is_completed(s) for s in workflow_stages):
            # If project isn't 'completed' but all stages are, it implies it's ready for finalization
            # or has finished the defined flow. Returning None is consistent.
            return None

        # Default to the first stage if no state indicates otherwise (should be handled by _initial_state)
        return workflow_stages[0]

    def finalize_project(self):
        # Mark the "project_finalization" stage as completed first
        # This ensures that is_completed("project_finalization") will be true
        # when the orchestrator checks all stages from its canonical list.
        self.complete_stage("project_finalization", artifacts={"summary": "Project finalized successfully by ProjectStateManager."})
        # Note: complete_stage already calls self.save_state() and adds to error_summary.
        # So, the explicit error_summary.add below might be redundant if complete_stage's message is sufficient.
        # However, keeping it for clarity or if a more specific message is desired from finalize_project itself.

        self.state["status"] = "completed" # Set overall project status
        self.state["completed_at"] = datetime.utcnow().isoformat()

        # This will add another entry to error_summary for "project_finalization" or update if stage already added.
        # ErrorSummary logic might need to handle duplicate stage entries if that's an issue,
        # or ensure complete_stage's message is what we want.
        # For now, let's assume ErrorSummary can handle it or it's a minor duplication.
        # To avoid exact duplicate message, let's make this one slightly different.
        self.error_summary.add("project_finalization", True, "Overall project status marked as COMPLETED.")

        self.save_state() # Ensure final status and timestamp are saved.

    def get_summary(self):
        return self.error_summary

    @staticmethod
    def list_projects():
        projects_list = []
        if not PROJECTS_ROOT.exists() or not PROJECTS_ROOT.is_dir():
            return []

        for item in PROJECTS_ROOT.iterdir():
            if item.is_dir():
                project_key = item.name # directory name is the key
                project_path = item
                state_file_path = project_path / "state.json"

                # Default values
                status = "Error - State file missing"
                # Default project name from key, can be overridden by state.json
                project_name_from_state = project_key.replace('_', ' ').title()
                last_updated = "N/A"
                error_message_str = None
                rich_name_prefix = "" # Default to no prefix

                if state_file_path.exists() and state_file_path.is_file():
                    try:
                        state_json = json.loads(state_file_path.read_text())
                        status = state_json.get("status", "Unknown")
                        project_name_from_state = state_json.get("project_name", project_name_from_state)

                        # Get last updated time, fallback to created_at
                        raw_last_updated = state_json.get("updated_at", state_json.get("created_at", "N/A"))
                        if isinstance(raw_last_updated, str) and raw_last_updated != "N/A":
                            try:
                                dt_obj = datetime.fromisoformat(raw_last_updated.replace("Z", "+00:00"))
                                last_updated = dt_obj.strftime("%Y-%m-%d %H:%M:%S %Z").strip()
                            except ValueError:
                                last_updated = raw_last_updated # Keep as is if parsing fails
                        else:
                            last_updated = "N/A"

                        if status == "failed":
                            error_summary_list = state_json.get("error_summary", [])
                            if isinstance(error_summary_list, list) and error_summary_list:
                                for record in reversed(error_summary_list): # Get the latest error
                                    if isinstance(record, dict) and not record.get("success", True):
                                        error_message_str = record.get("message", "No specific error message found.")
                                        break
                                if error_message_str is None:
                                     error_message_str = "Failed, but no specific error message recorded in summary."
                            else:
                                error_message_str = "Failed, error summary not available or empty."

                    except json.JSONDecodeError:
                        status = "Error - State file corrupted"
                        error_message_str = "State.json is corrupted."
                        last_updated = "N/A" # Reset as state is corrupt
                else: # State file does not exist
                    error_message_str = "State.json is missing for this project."


                # Set rich_name_prefix based on status
                if status == "completed":
                    rich_name_prefix = "✅ "
                elif status == "failed":
                    rich_name_prefix = "❌ "
                elif status.startswith("Error -") or status == "Unknown":
                    rich_name_prefix = "⚠️ "
                # else: in_progress or other statuses might not need a prefix or could have a different one

                projects_list.append({
                    "key": project_key,
                    "name": project_name_from_state,
                    "status": status,
                    "rich_name": f"{rich_name_prefix}{project_name_from_state}",
                    "last_updated": last_updated,
                    "path": str(project_path.resolve()),
                    "error_message": error_message_str
                })

        # Sort projects: failed first, then error statuses, then completed, then others, then by name
        def sort_key_func(p):
            status_lower = p['status'].lower()
            if 'failed' in status_lower: # Catches "failed"
                return 0
            elif status_lower.startswith('error -'): # Catches "Error - State file missing/corrupted"
                return 1
            elif 'completed' in status_lower: # Catches "completed"
                return 2
            elif 'unknown' in status_lower : # Catches "Unknown"
                return 3
            else: # For "in_progress", etc.
                return 4

        projects_list.sort(key=lambda p: (sort_key_func(p), p['name']))
        return projects_list
