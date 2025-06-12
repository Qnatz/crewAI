# Configuration for MobileProjectCoordinatorAgent

delegates_android = [
    "AndroidUIAgent",
    "AndroidAPIClientAgent",
    "AndroidStorageAgent",
]

delegates_ios = [
    "iOSUIAgent",
    "iOSAPIClientAgent",
    "iOSStorageAgent",
]

delegates_shared = [
    "SyncAgent",    # This would be the one from backend or a dedicated mobile sync
    "LoggerAgent",
    "TesterAgent",
]

# Logic for platform detection and flow management will be configured here.
# Example:
# platform_detection_logic = "based_on_input_parameters" # or "user_specification"
#
# default_flow_android = delegates_android + delegates_shared
# default_flow_ios = delegates_ios + delegates_shared
#
# conditional_flows = {
#     "offline_logic_needed": True, # Example condition
#     "agents_if_true": ["SyncAgent"] # Ensure SyncAgent is part of the flow
# }

# Combined list for easier reference in agent, actual delegation might be more dynamic
all_possible_delegates = list(set(delegates_android + delegates_ios + delegates_shared))
