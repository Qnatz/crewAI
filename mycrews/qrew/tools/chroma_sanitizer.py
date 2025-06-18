# mycrews/qrew/tools/chroma_sanitizer.py

def sanitize_metadata(meta: dict) -> dict:
    """
    Ensure all metadata values are of type str, int, float, or bool.
    - Lists become comma-separated strings (empty lists become "none").
    - None values are dropped.
    - Other types are stringified.
    """
    clean = {}
    for key, value in meta.items():
        if isinstance(value, (str, int, float, bool)):
            clean[key] = value
        elif isinstance(value, list):
            clean[key] = ", ".join(map(str, value)) if value else "none"
        elif value is None:
            continue  # Skip None values
        else:
            clean[key] = str(value)
    return clean
