# mycrews/qrew/llm_config.py
import os
from crewai import LLM
from typing import Optional # For type hinting LLM | None

# List to store initialization statuses
llm_initialization_statuses = []

# Define the new target model strings
M1_FLASH_LATEST = "gemini/gemini-1.5-flash-latest"
M2_PRO_LATEST = "gemini/gemini-1.5-pro-latest"
M3_FLASH_2_5 = "gemini/gemini-2.5-flash" # Assuming this is a valid model identifier

# Define the mapping of agent identifiers to specific Gemini model strings
MODEL_BY_AGENT = {
    # --- High-capability/Orchestration/Planning Agents (M2) ---
    "idea_interpreter_agent": {"model": M2_PRO_LATEST, "max_tokens": 2500, "temperature": 0.7},
    "project_architect_agent": {"model": M2_PRO_LATEST, "max_tokens": 3000, "temperature": 0.7},
    "taskmaster_agent": {"model": M2_PRO_LATEST, "max_tokens": 2000, "temperature": 0.7},
    "final_assembler_agent": {"model": M2_PRO_LATEST, "max_tokens": 3000, "temperature": 0.6},
    "execution_manager_agent": {"model": M2_PRO_LATEST, "max_tokens": 2000, "temperature": 0.7},
    "tech_vetting_council_agent": {"model": M2_PRO_LATEST, "max_tokens": 2500, "temperature": 0.7},

    # Lead Agents (Coordinators) (M2)
    "backend_project_coordinator_agent": {"model": M2_PRO_LATEST, "max_tokens": 2500, "temperature": 0.7},
    "devops_and_integration_coordinator_agent": {"model": M2_PRO_LATEST, "max_tokens": 2500, "temperature": 0.7},
    "mobile_project_coordinator_agent": {"model": M2_PRO_LATEST, "max_tokens": 2500, "temperature": 0.7},
    "offline_support_coordinator_agent": {"model": M2_PRO_LATEST, "max_tokens": 2000, "temperature": 0.7},
    "web_project_coordinator_agent": {"model": M2_PRO_LATEST, "max_tokens": 2500, "temperature": 0.7},
    "auth_coordinator_agent": {"model": M2_PRO_LATEST, "max_tokens": 2000, "temperature": 0.7},

    # --- Specialized Implementation/Utility Agents ---
    # Auth Agents
    "otp_verifier_agent": {"model": M1_FLASH_LATEST, "max_tokens": 1000, "temperature": 0.4},

    # Backend Agents (Distribute M1 & M3)
    "api_creator_agent": {"model": M1_FLASH_LATEST, "max_tokens": 3500, "temperature": 0.3},
    "auth_agent_backend": {"model": M3_FLASH_2_5, "max_tokens": 3000, "temperature": 0.3},
    "config_agent_backend": {"model": M1_FLASH_LATEST, "max_tokens": 2000, "temperature": 0.4},
    "data_model_agent_backend": {"model": M3_FLASH_2_5, "max_tokens": 3000, "temperature": 0.4},
    "queue_agent_backend": {"model": M1_FLASH_LATEST, "max_tokens": 2500, "temperature": 0.4},
    "storage_agent_backend": {"model": M3_FLASH_2_5, "max_tokens": 2500, "temperature": 0.4},
    "sync_agent_backend": {"model": M1_FLASH_LATEST, "max_tokens": 2500, "temperature": 0.4},

    # Dev Utilities Agents (Distribute M1 & M3)
    "code_writer_agent": {"model": M3_FLASH_2_5, "max_tokens": 4000, "temperature": 0.3},
    "debugger_agent": {"model": M1_FLASH_LATEST, "max_tokens": 2000, "temperature": 0.5},
    "logger_agent_devutils": {"model": M1_FLASH_LATEST, "max_tokens": 1500, "temperature": 0.4},
    "tester_agent_devutils": {"model": M3_FLASH_2_5, "max_tokens": 2500, "temperature": 0.5},

    # DevOps Agent
    "devops_agent": {"model": M1_FLASH_LATEST, "max_tokens": 3000, "temperature": 0.4},

    # Mobile Agents (Android - M1 & M3)
    "android_api_client_agent": {"model": M1_FLASH_LATEST, "max_tokens": 3000, "temperature": 0.3},
    "android_storage_agent": {"model": M3_FLASH_2_5, "max_tokens": 2500, "temperature": 0.4},
    "android_ui_agent": {"model": M1_FLASH_LATEST, "max_tokens": 3500, "temperature": 0.4},
    # Mobile Agents (iOS - M1 & M3)
    "ios_api_client_agent": {"model": M1_FLASH_LATEST, "max_tokens": 3000, "temperature": 0.3},
    "ios_storage_agent": {"model": M3_FLASH_2_5, "max_tokens": 2500, "temperature": 0.4},
    "ios_ui_agent": {"model": M1_FLASH_LATEST, "max_tokens": 3500, "temperature": 0.4},

    # Offline Agents
    "local_storage_agent_offline": {"model": M1_FLASH_LATEST, "max_tokens": 2000, "temperature": 0.4},
    "sync_agent_offline": {"model": M3_FLASH_2_5, "max_tokens": 2500, "temperature": 0.4},

    # Web Agents (Distribute M1 & M3)
    "asset_manager_agent_web": {"model": M1_FLASH_LATEST, "max_tokens": 2000, "temperature": 0.4},
    "dynamic_page_builder_agent_web": {"model": M3_FLASH_2_5, "max_tokens": 3500, "temperature": 0.4},
    "static_page_builder_agent_web": {"model": M1_FLASH_LATEST, "max_tokens": 3000, "temperature": 0.4},

    # Tech Stack Committee (Distribute M1 & M3, council lead is M2)
    "constraint_checker_agent_tech_committee": {"model": M1_FLASH_LATEST, "max_tokens": 1500, "temperature": 0.6},
    "documentation_writer_agent_tech_committee": {"model": M3_FLASH_2_5, "max_tokens": 3000, "temperature": 0.7},
    "stack_advisor_agent_tech_committee": {"model": M1_FLASH_LATEST, "max_tokens": 2000, "temperature": 0.7},

    # Tools (if a tool needed its own LLM)
    "knowledge_base_tool_summarizer": {"model": M1_FLASH_LATEST, "max_tokens": 1500, "temperature": 0.6},

    # --- Crew-level LLMs (can mirror lead or be specific) ---
    "backend_development_crew": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},
    "devops_crew": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},
    "full_stack_crew": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},
    "mobile_development_crew": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},
    "offline_support_crew": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},
    "code_writing_crew": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},
    "final_assembly_crew": {"model": M2_PRO_LATEST, "max_tokens": 2500, "temperature": 0.6}, # Promoted
    "web_development_crew": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},

    # --- Default LLMs ---
    "default_crew_llm": {"model": M3_FLASH_2_5, "max_tokens": 2000, "temperature": 0.6},
    "default_agent_llm": {"model": M1_FLASH_LATEST, "max_tokens": 1500, "temperature": 0.5}
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

    agent_config = MODEL_BY_AGENT.get(agent_identifier)
    if not agent_config:
        # print(f"No specific config for agent '{agent_identifier}'. Using default config key: '{default_model_key}'.") # Suppressed
        agent_config = MODEL_BY_AGENT.get(default_model_key)
        if not agent_config:
            # print(f"Error: Default config key '{default_model_key}' not found. Cannot configure LLM for '{agent_identifier}'.") # Suppressed
            llm_initialization_statuses.append((f"CONFIG_ERROR_FOR_{agent_identifier}", False))
            return None

    model_str = agent_config.get("model")
    max_tokens_val = agent_config.get("max_tokens")
    temp_val = agent_config.get("temperature")

    if not model_str:
        # print(f"Error: 'model' not specified in config for '{agent_identifier}'. Config: {agent_config}") # Suppressed
        llm_initialization_statuses.append((f"MODEL_UNDEFINED_FOR_{agent_identifier}_IN_CONFIG_{agent_config.get('model', 'N/A')}", False))
        return None

    # Construct llm_params, only including max_tokens and temperature if they are not None
    # Default num_retries is already handled by LiteLLM/CrewAI's LLM class if not specified.
    # Adding it explicitly like num_retries=3.
    llm_params = {"model": model_str, "num_retries": 3}
    if max_tokens_val is not None:
        llm_params["max_tokens"] = max_tokens_val
    if temp_val is not None:
        llm_params["temperature"] = temp_val

    # print(f"Configuring LLM for agent '{agent_identifier}' with params: {llm_params}") # Suppressed

    try:
        llm = LLM(**llm_params)
        # print(f"Successfully initialized LLM for agent '{agent_identifier}' with model '{model_str}'.") # Suppressed
        llm_initialization_statuses.append((model_str, True))
        return llm
    except Exception as e:
        # print(f"Failed to initialize LLM for agent '{agent_identifier}' with model '{model_str}': {e}") # Suppressed
        llm_initialization_statuses.append((model_str, False))
        return None

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
