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
        if not PROJECTS_INDEX.exists():
            return []

        try:
            index_data = json.loads(PROJECTS_INDEX.read_text())
        except json.JSONDecodeError:
            return [] # Index is corrupted

        projects_list = []
        for project_key, project_info in index_data.items():
            project_name = project_info.get("name", "Unknown Project")
            project_id = project_info.get("id", project_key) # Use key if id is missing
            project_path_str = project_info.get("path")
            error_message_str = None
            rich_name_prefix = ""
            state_data = None # Initialize state_data

            if not project_path_str:
                status = "Error - Path missing"
                last_updated = "N/A"
                # No state_data, so error_message_str remains None, rich_name_prefix empty
            else:
                state_file_path = Path(project_path_str) / "state.json"
                if state_file_path.exists():
                    try:
                        state_data = json.loads(state_file_path.read_text())
                        status = state_data.get("status", "Unknown")
                        last_updated = state_data.get("updated_at", state_data.get("created_at", "N/A"))
                        # Attempt to parse and reformat last_updated
                        try:
                            if isinstance(last_updated, str):
                                 dt_obj = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                                 last_updated = dt_obj.strftime("%Y-%m-%d %H:%M:%S %Z")
                        except (ValueError, AttributeError):
                            pass # Keep original last_updated string
                    except json.JSONDecodeError:
                        status = "Error - State file corrupted"
                        last_updated = "N/A" # Reset last_updated as state is corrupt
                else:
                    status = "Error - State file missing"
                    last_updated = "N/A" # Reset last_updated as state is missing

            # Determine rich_name_prefix and error_message_str based on status and state_data
            if status == "completed":
                rich_name_prefix = "✅ "
            elif status == "failed":
                rich_name_prefix = "❌ "
                if state_data and "error_summary" in state_data:
                    error_summary_list = state_data["error_summary"]
                    if isinstance(error_summary_list, list) and error_summary_list:
                        for record in reversed(error_summary_list):
                            if isinstance(record, dict) and not record.get("success", True):
                                error_message_str = record.get("message", "No specific error message found.")
                                break
                        if error_message_str is None: # No failure message found in list
                            error_message_str = "Failed, but no specific error message recorded in summary."
                    else: # Empty or malformed error_summary
                        error_message_str = "Failed, error summary not available or empty."
                elif status == "failed": # Ensure message if state_data was problematic but status is 'failed'
                    error_message_str = "Failed, error summary not found in state file or state file issue."


            projects_list.append({
                "key": project_id,
                "name": project_name,
                "status": status,
                "rich_name": f"{rich_name_prefix}{project_name}",
                "last_updated": last_updated,
                "path": project_path_str if project_path_str else "N/A",
                "error_message": error_message_str
            })

        # Sort projects: failed first, then completed, then others, then by name
        def sort_key_func(p):
            if p['status'] == 'failed':
                return 0
            elif p['status'] == 'completed':
                return 1
            # Group error statuses (like missing path/corrupted file) after 'other' normal statuses
            elif 'Error -' in p['status']:
                return 3
            else: # For "in_progress", "Unknown", etc.
                return 2

        projects_list.sort(key=lambda p: (sort_key_func(p), p['name']))
        return projects_list
