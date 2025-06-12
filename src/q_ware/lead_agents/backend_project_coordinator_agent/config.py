# Configuration for BackendProjectCoordinatorAgent
# Defines which sub-agents this coordinator can delegate to.

delegates = [
    "AuthAgent",
    "DataModelAgent",
    "APICreatorAgent",
    "SyncAgent",
    "DebuggerAgent",
    "TesterAgent",
]

# Further configuration for decision making (e.g., DB stack),
# conditional flows (e.g., if offline sync is flagged),
# and task sequencing.
