# Configuration for OfflineSupportCoordinatorAgent

delegates = [
    "LocalStorageAgent", # General local storage
    "SyncAgent",         # Could be backend or local-first version
    "AndroidStorageAgent", # Example platform-specific
    "iOSStorageAgent",     # Example platform-specific
    # Potentially a web-specific local storage agent if different from LocalStorageAgent
]

# Configuration would detail how to choose between storage agents
# and the sequence of operations for enabling offline mode,
# handling data sync, and conflict resolution.
# Example:
# app_type_specific_storage = {
#     "web": "LocalStorageAgent", # or specific web storage agent
#     "android": "AndroidStorageAgent",
#     "ios": "iOSStorageAgent"
# }
#
# offline_setup_flow = [
#     "select_storage_agent_based_on_app_type",
#     "configure_local_schema",
#     "setup_sync_agent_for_reconciliation",
#     "implement_fallback_mechanisms"
# ]
