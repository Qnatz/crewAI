# mycrews/qrew/llm_config.py
import os
from crewai import LLM
from typing import Optional # For type hinting LLM | None

# List to store initialization statuses
llm_initialization_statuses = []

# Define New User-Provided Gemini Model Constants
GEMINI_1_5_PRO = "gemini/gemini-1.5-pro"
GEMINI_1_5_FLASH = "gemini/gemini-1.5-flash"
GEMINI_2_0_FLASH = "gemini/gemini-2.0-flash"
GEMINI_2_0_FLASH_LITE_001 = "gemini/gemini-2.0-flash-lite-001"
GEMINI_2_5_FLASH_PREVIEW_04_17 = "gemini/gemini-2.5-flash-preview-04-17"
GEMINI_2_5_PRO_EXP_03_25 = "gemini/gemini-2.5-pro-exp-03-25"

# Comment out or remove old Gemini constants
# NEW_PRO_MODEL = "gemini/gemini-2.5-pro-preview-06-05"
# NEW_FLASH_MODEL = "gemini/gemini-2.5-flash-preview-05-20"
# PRO_MODEL_PRIMARY = "gemini/gemini-1.5-pro-002"  # Assuming this is a valid identifier for the latest Pro
# FLASH_STABLE_ALIAS = "gemini/gemini-1.5-flash"    # Alias for latest stable Flash
# FLASH_OLDER_STABLE = "gemini/gemini-2.0-flash"   # Older stable Flash (example, use actual if different)

# Old constants M1, M2, M3 are removed as their roles are superseded by the new constants and logic.

# Create a Comprehensive List of New Gemini Models
USER_SPECIFIED_GEMINI_MODELS = [
    {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
    {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
    {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
    {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7},
    {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
    {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
]

# Define the mapping of agent identifiers to a list of model configurations (for fallback)
MODEL_BY_AGENT = {
    # --- High-capability/Orchestration/Planning Agents ---
    "idea_interpreter_agent": [
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "project_architect_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7}
    ],
    "taskmaster_agent": [
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7}
    ],
    "final_assembler_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "execution_manager_agent": [
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7}
    ],
    "tech_vetting_council_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7}
    ],

    # Lead Agents (Coordinators)
    "backend_project_coordinator_agent": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7}
    ],
    "devops_and_integration_coordinator_agent": [
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "mobile_project_coordinator_agent": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "offline_support_coordinator_agent": [
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "web_project_coordinator_agent": [
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "auth_coordinator_agent": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7}
    ],

    # --- Specialized Implementation/Utility Agents ---
    "otp_verifier_agent": [
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "api_creator_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "auth_agent_backend": [
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7}
    ],
    "config_agent_backend": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "data_model_agent_backend": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7}
    ],
    "queue_agent_backend": [
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "storage_agent_backend": [
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "sync_agent_backend": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "code_writer_agent": [
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "debugger_agent": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7}
    ],
    "logger_agent_devutils": [
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "tester_agent_devutils": [
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "devops_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7}
    ],
    "android_api_client_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "android_ui_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "ios_api_client_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "ios_ui_agent": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "android_storage_agent": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "ios_storage_agent": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "local_storage_agent_offline": [
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "sync_agent_offline": [
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "asset_manager_agent_web": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "dynamic_page_builder_agent_web": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7}
    ],
    "static_page_builder_agent_web": [
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "constraint_checker_agent_tech_committee": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "documentation_writer_agent_tech_committee": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "stack_advisor_agent_tech_committee": [
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7}
    ],
    "knowledge_base_tool_summarizer": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],

    # --- Crew-level LLMs ---
    "final_assembly_crew": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "backend_development_crew": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7}
    ],
    "devops_crew": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "full_stack_crew": [
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "mobile_development_crew": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "offline_support_crew": [
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ],
    "code_writing_crew": [
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "web_development_crew": [
        {"model": GEMINI_2_5_FLASH_PREVIEW_04_17, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_5_PRO_EXP_03_25, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],

    # --- Default LLMs ---
    "default_crew_llm": [
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_PRO, "max_tokens": 3000, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7}
    ],
    "default_agent_llm": [
        {"model": GEMINI_2_0_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_1_5_FLASH, "max_tokens": 2500, "temperature": 0.7},
        {"model": GEMINI_2_0_FLASH_LITE_001, "max_tokens": 2000, "temperature": 0.7}
    ]
}

def get_llm_for_agent(agent_identifier: str, default_model_key: str = "default_agent_llm") -> Optional[LLM]:
    """
    Retrieves a configured LLM instance for a specific agent.

    Args:
        agent_identifier: A unique string identifying the agent (e.g., its role or variable name).
        default_model_key: The key in MODEL_BY_AGENT to use if agent_identifier is not found.
                           Defaults to "default_agent_llm".

    Returns:
        An LLM instance or None if configuration fails or API key is missing.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        llm_initialization_statuses.append((f"API_KEY_MISSING_FOR_{agent_identifier}", False))
        return None

    model_configs_list = MODEL_BY_AGENT.get(agent_identifier)
    if not model_configs_list:
        # print(f"No specific config list for agent '{agent_identifier}'. Using default config key: '{default_model_key}'.") # Suppressed
        model_configs_list = MODEL_BY_AGENT.get(default_model_key)
        if not model_configs_list:
            # print(f"Error: Default config key '{default_model_key}' not found. Cannot configure LLM for '{agent_identifier}'.") # Suppressed
            llm_initialization_statuses.append((f"CONFIG_LIST_ERROR_FOR_{agent_identifier}", False))
            return None

    if not isinstance(model_configs_list, list):
        # print(f"Error: Agent configuration for '{agent_identifier}' is not a list. Found: {type(model_configs_list)}") # Suppressed
        llm_initialization_statuses.append((f"CONFIG_NOT_LIST_FOR_{agent_identifier}", False))
        return None

    for i, agent_config in enumerate(model_configs_list):
        model_str = agent_config.get("model")
        max_tokens_val = agent_config.get("max_tokens")
        temp_val = agent_config.get("temperature")

        if not model_str:
            # print(f"Error: 'model' not specified in config entry {i} for '{agent_identifier}'. Config: {agent_config}") # Suppressed
            # Log this attempt as a failure for this specific model string if available, else generic
            llm_initialization_statuses.append((f"MODEL_UNDEFINED_IN_LIST_FOR_{agent_identifier}_{i}", False))
            continue # Try next model in the list

        llm_params = {"model": model_str, "num_retries": 3} # num_retries can also be configurable
        if max_tokens_val is not None:
            llm_params["max_tokens"] = max_tokens_val
        if temp_val is not None:
            llm_params["temperature"] = temp_val

        # print(f"Attempting to initialize LLM for agent '{agent_identifier}' with model config {i+1}/{len(model_configs_list)}: {llm_params}") # Suppressed
        try:
            llm = LLM(**llm_params)
            # If LLM instantiation is successful, consider it primarily successful for this configuration.
            # print(f"Successfully initialized LLM for agent '{agent_identifier}' with model '{model_str}'.") # Suppressed
            llm_initialization_statuses.append((f"{model_str} (initialized)", True))
            return llm # Return the successfully initialized LLM
        except Exception as e_init:
            # print(f"Failed to initialize LLM for agent '{agent_identifier}' with model '{model_str}' (Attempt {i+1}/{len(model_configs_list)}): {e_init}") # Suppressed
            llm_initialization_statuses.append((f"{model_str} (init_exception: {str(e_init)[:50]})", False))
            # Continue to the next model in the list if initialization fails

    # print(f"All model configurations failed for agent '{agent_identifier}'.") # Suppressed
    return None # Return None if all models in the list fail

# Global default LLM for general use by Crews or as a fallback if an agent-specific one isn't assigned directly.
default_crew_llm = get_llm_for_agent("default_crew_llm") # default_model_key will be "default_agent_llm" if "default_crew_llm" not found

# The initialization of default_crew_llm itself will append to llm_initialization_statuses via get_llm_for_agent.
# So, no separate print or status update is needed here for default_crew_llm's own initialization.
# We can add a general print statement that confirms its status based on the list, if desired, for clarity.

if not default_crew_llm:
    # This specific print is useful because it indicates a critical failure for the default LLM.
    # The status list will reflect this, but an explicit message here is fine.
    # print("llm_config.py: `default_crew_llm` (and thus `default_llm`) could not be initialized. This is critical.") # Suppressed
    # Ensure its status is logged if get_llm_for_agent failed before appending (e.g. API key missing early)
    # However, get_llm_for_agent should handle appending its own failure.
    pass # The failure is recorded in llm_initialization_statuses
else:
    # This print is mostly for confirmation during script load. The status list is the source of truth for display.
    # print(f"llm_config.py: `default_crew_llm` (and `default_llm`) initialization attempt completed. Check status list for details.") # Suppressed
    pass

# Note: The old `default_llm` variable is no longer the primary way to get LLMs.
# Agents/Crews should ideally call `get_llm_for_agent(their_identifier)` or be passed an LLM.
# `default_crew_llm` is provided as a general fallback, particularly for Crew instances.
# For clarity in main.py, it might import and use `default_crew_llm` for the crew.
# Or, main.py could choose a specific agent's LLM for the crew if that's more appropriate.
# This file no longer defines a single `default_llm` for all purposes.
# However, to maintain compatibility with how `main.py` currently imports `default_llm`,
# we can alias `default_crew_llm` to `default_llm` for now.
default_llm = default_crew_llm
# The status of default_llm is already captured by the call to get_llm_for_agent for 'default_crew_llm'.
# No need for further status updates or prints here regarding default_llm specifically,
# as they would be redundant with the get_llm_for_agent logging and status list.

# Final check for clarity in logs (optional)
# found_default_status = False
# for name, status in llm_initialization_statuses:
#     if name == "default_crew_llm" or name.startswith("default_crew_llm "): # Handles the modified name if default was used
#         found_default_status = True
#         print(f"llm_config.py: `default_llm` (alias for `default_crew_llm`) status in list: {'Ready' if status else 'Failed'}.")
#         break
# if not found_default_status:
#     print("llm_config.py: Status for `default_crew_llm` not found in list, this might indicate an issue before status recording.")

# The print statements within get_llm_for_agent and the one for default_crew_llm initialization failure
# are sufficient for console feedback during module load. The UI display will use llm_initialization_statuses.
