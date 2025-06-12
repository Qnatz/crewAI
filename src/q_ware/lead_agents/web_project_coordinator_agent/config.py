# Configuration for WebProjectCoordinatorAgent
# Defines which sub-agents this coordinator can delegate to.

delegates = [
    "StaticPageBuilderAgent",
    "DynamicPageBuilderAgent",
    "AssetManagerAgent",
    "APICreatorAgent", # (if SSR/API integration needed)
    "TesterAgent",
    "CodeWriterAgent",
]

# Further configuration for sequencing, context passing, etc. can be added here.
# For example, defining flows or conditional logic for delegation.
# flow = {
#     "determine_site_type": {
#         "condition": "site_type == 'static'",
#         "next_task_if_true": "sequence_static_build",
#         "next_task_if_false": "sequence_dynamic_build"
#     },
#     "sequence_static_build": [
#         "AssetManagerAgent",
#         "StaticPageBuilderAgent",
#         "TesterAgent"
#     ],
#     # ... and so on
# }
