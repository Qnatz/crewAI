# mycrews/qrew/project_manager.py
import os
import json
import hashlib
from pathlib import Path

# Paths are relative to this file's location, so projects_index.json
# and the projects/ directory will be inside mycrews/qrew/
PROJECTS_INDEX = Path("projects_index.json")
PROJECTS_ROOT = Path("projects/")

def _load_index():
    if PROJECTS_INDEX.exists():
        try:
            return json.loads(PROJECTS_INDEX.read_text())
        except json.JSONDecodeError: # Handle empty or corrupted file
            return {}
    return {}

def _save_index(index):
    PROJECTS_INDEX.write_text(json.dumps(index, indent=2))

def _slugify(name: str) -> str:
    safe = "".join(c if c.isalnum() else "_" for c in name).lower()
    return safe[:50]

def get_or_create_project(name: str) -> dict:
    """
    Look up an existing project by name (or similar hash),
    or create a new folder under projects/<slug>_<shorthash>
    within the mycrews/qrew/ directory.
    Returns a dict with 'name', 'id', and 'path'.
    """
    index = _load_index()
    name_hash = hashlib.sha1(name.encode()).hexdigest()[:8]
    key = f"{_slugify(name)}_{name_hash}"

    if key in index:
        proj = index[key]
        proj_path = Path(proj["path"]) # Path stored is already relative to execution
        status = "continuing"
    else:
        # Ensure PROJECTS_ROOT directory exists
        PROJECTS_ROOT.mkdir(parents=True, exist_ok=True) # Ensures mycrews/qrew/projects/ exists

        proj_path = PROJECTS_ROOT / key
        proj_path.mkdir(parents=True, exist_ok=True) # Ensures mycrews/qrew/projects/some_project/ exists

        proj = {"name": name, "id": key, "path": str(proj_path)}
        index[key] = proj
        _save_index(index)
        status = "new"
    return {"status": status, **proj}
