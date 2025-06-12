# project_manager.py
import os
import json
import hashlib
from pathlib import Path

PROJECTS_INDEX = Path("projects_index.json")
PROJECTS_ROOT = Path("projects/")

def _load_index():
    if PROJECTS_INDEX.exists():
        return json.loads(PROJECTS_INDEX.read_text())
    return {}

def _save_index(index):
    PROJECTS_INDEX.write_text(json.dumps(index, indent=2))

def _slugify(name: str) -> str:
    safe = "".join(c if c.isalnum() else "_" for c in name).lower()
    return safe[:50]

def get_or_create_project(name: str) -> dict:
    """
    Look up an existing project by name (or similar hash),
    or create a new folder under projects/<slug>_<shorthash>.
    Returns a dict with 'name', 'id', and 'path'.
    """
    index = _load_index()
    # Use a hash of the name to detect “same” projects
    name_hash = hashlib.sha1(name.encode()).hexdigest()[:8]
    key = f"{_slugify(name)}_{name_hash}"

    if key in index:
        proj = index[key]
        # Ensure the path is a Path object for consistency, though it's stored as str
        proj_path = Path(proj["path"])
        status = "continuing"
    else:
        # Ensure PROJECTS_ROOT is a Path object and then create the new project path
        proj_path = PROJECTS_ROOT / key
        proj_path.mkdir(parents=True, exist_ok=True)
        proj = {"name": name, "id": key, "path": str(proj_path)}
        index[key] = proj
        _save_index(index)
        status = "new"
    return {"status": status, **proj}
