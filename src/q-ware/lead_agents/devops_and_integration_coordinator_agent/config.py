# Configuration for DevOpsAndIntegrationCoordinatorAgent

delegates = [
    "TesterAgent",
    "DebuggerAgent",
    "LoggerAgent",
    # "CICDHandlerAgent", # Future agent
]

# Configuration would detail the integration pipeline,
# how logs are collected and aggregated,
# and the criteria for test/debug passes.
# Example:
# pre_deploy_pipeline = [
#     "collect_all_agent_logs",
#     "run_integration_tests_via_tester_agent",
#     "run_debug_passes_via_debugger_agent_on_failure",
#     "report_status_to_cicd_system" # Future integration
# ]
#
# log_collection_strategy = "aggregate_and_forward_to_central_logging"
