# mycrews/qrew/llm_config.py
import os
from crewai import LLM
from typing import Optional # For type hinting LLM | None

# Define the mapping of agent identifiers to specific Gemini model strings
MODEL_BY_AGENT = {
    # Auth Agents
    "auth_coordinator_agent": "gemini/gemini-2.0-flash-001",
    "otp_verifier_agent": "gemini/gemini-2.0-flash-001",

    # Backend Agents
    "api_creator_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "auth_agent_backend": "gemini/gemini-2.5-flash-preview-04-17",
    "config_agent_backend": "gemini/gemini-2.5-flash-preview-04-17",
    "data_model_agent_backend": "gemini/gemini-2.0-flash-001",
    "queue_agent_backend": "gemini/gemini-2.0-flash-001",
    "storage_agent_backend": "gemini/gemini-2.0-flash-001",
    "sync_agent_backend": "gemini/gemini-2.5-flash-preview-04-17",

    # Dev Utilities Agents
    "code_writer_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "debugger_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "logger_agent_devutils": "gemini/gemini-2.0-flash-001",
    "tester_agent_devutils": "gemini/gemini-2.5-flash-preview-04-17",

    # DevOps Agent
    "devops_agent": "gemini/gemini-1.5-flash",

    # Mobile Agents (Android)
    "android_api_client_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "android_storage_agent": "gemini/gemini-2.0-flash-001",
    "android_ui_agent": "gemini/gemini-2.5-flash-preview-04-17",
    # Mobile Agents (iOS)
    "ios_api_client_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "ios_storage_agent": "gemini/gemini-2.0-flash-001",
    "ios_ui_agent": "gemini/gemini-2.5-flash-preview-04-17",

    # Offline Agents
    "local_storage_agent_offline": "gemini/gemini-2.0-flash-lite-001",
    "sync_agent_offline": "gemini/gemini-2.0-flash-lite-001", # Adjusted as per resource constraints theme

    # Web Agents
    "asset_manager_agent_web": "gemini/gemini-2.0-flash-001", # Adjusted as asset management might be less complex
    "dynamic_page_builder_agent_web": "gemini/gemini-1.5-flash",
    "static_page_builder_agent_web": "gemini/gemini-2.0-flash-001",

    # Crews (using generic keys for crew-level LLM if needed, can be same as lead agents)
    "backend_development_crew": "gemini/gemini-2.5-flash-preview-04-17",
    "devops_crew": "gemini/gemini-2.5-flash-preview-04-17",
    "full_stack_crew": "gemini/gemini-2.5-flash-preview-04-17",
    "mobile_development_crew": "gemini/gemini-2.5-flash-preview-04-17",
    "offline_support_crew": "gemini/gemini-2.0-flash-lite-001", # Crew dealing with offline might use lite
    "code_writing_crew": "gemini/gemini-2.5-flash-preview-04-17",
    "final_assembly_crew": "gemini/gemini-2.5-flash-preview-04-17",
    "web_development_crew": "gemini/gemini-2.5-flash-preview-04-17",

    # Lead Agents
    "backend_project_coordinator_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "devops_and_integration_coordinator_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "mobile_project_coordinator_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "offline_support_coordinator_agent": "gemini/gemini-2.0-flash-lite-001", # Coordinator for offline might use lite
    "web_project_coordinator_agent": "gemini/gemini-2.5-flash-preview-04-17",

    # Orchestrators
    "execution_manager_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "final_assembler_agent": "gemini/gemini-2.5-flash-preview-04-17",
    "idea_interpreter_agent": "gemini/gemini-2.5-flash-preview-04-17", # High capability needed
    "project_architect_agent": "gemini/gemini-1.5-flash", # Changed for reliability, was gemini-2.5-flash-preview-04-17
    # Tech Stack Committee
    "constraint_checker_agent_tech_committee": "gemini/gemini-2.0-flash-001",
    "documentation_writer_agent_tech_committee": "gemini/gemini-2.0-flash-001",
    "stack_advisor_agent_tech_committee": "gemini/gemini-2.5-flash-preview-04-17",
    "tech_vetting_council_agent": "gemini/gemini-2.5-flash-preview-04-17", # Main council agent

    # TaskMaster
    "taskmaster_agent": "gemini/gemini-1.5-flash", # High capability needed

    # Tools (if a tool needed its own LLM, e.g., for summarization within the tool)
    "knowledge_base_tool_summarizer": "gemini/gemini-2.0-flash-001",

    # Default for crews or agents not specifically listed / Fallback LLM
    "default_crew_llm": "gemini/gemini-1.5-flash", # Fallback, widely capable
    "default_agent_llm": "gemini/gemini-1.5-flash", # Fallback for any agent not in this map
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
        print(f"GEMINI_API_KEY not found in environment. Cannot initialize LLM for agent '{agent_identifier}'.")
        return None

    # Determine the model string: use agent-specific if defined, else use the model specified by default_model_key
    chosen_model_string = MODEL_BY_AGENT.get(agent_identifier)

    if not chosen_model_string:
        print(f"No specific model found for agent '{agent_identifier}'. Using default model key: '{default_model_key}'.")
        chosen_model_string = MODEL_BY_AGENT.get(default_model_key)
        if not chosen_model_string: # Should not happen if default_model_key is in MODEL_BY_AGENT
             print(f"Error: Default model key '{default_model_key}' not found in MODEL_BY_AGENT. Cannot configure LLM for '{agent_identifier}'.")
             return None


    print(f"Configuring LLM for agent '{agent_identifier}' with model: '{chosen_model_string}'...")

    try:
        # crewai.LLM handles API key via environment for supported models like Gemini
        llm = LLM(model=chosen_model_string)
        print(f"Successfully initialized LLM for agent '{agent_identifier}' with model '{chosen_model_string}'.")
        return llm
    except Exception as e:
        print(f"Failed to initialize LLM for agent '{agent_identifier}' with model '{chosen_model_string}': {e}")
        return None

# Global default LLM for general use by Crews or as a fallback if an agent-specific one isn't assigned directly.
# The "default_crew_llm" key in MODEL_BY_AGENT specifies which model this should be.
default_crew_llm = get_llm_for_agent("default_crew_llm", "gemini/gemini-1.5-flash") # Ensure "gemini/gemini-1.5-flash" is a fallback if key is missing

if not default_crew_llm:
    print("llm_config.py: `default_crew_llm` could not be initialized. Crews may need LLMs passed explicitly or rely on other fallbacks.")
else:
    print(f"llm_config.py: `default_crew_llm` initialized with model '{MODEL_BY_AGENT.get('default_crew_llm', 'gemini/gemini-1.5-flash')}'.")

# Note: The old `default_llm` variable is no longer the primary way to get LLMs.
# Agents/Crews should ideally call `get_llm_for_agent(their_identifier)` or be passed an LLM.
# `default_crew_llm` is provided as a general fallback, particularly for Crew instances.
# For clarity in main.py, it might import and use `default_crew_llm` for the crew.
# Or, main.py could choose a specific agent's LLM for the crew if that's more appropriate.
# This file no longer defines a single `default_llm` for all purposes.
# However, to maintain compatibility with how `main.py` currently imports `default_llm`,
# we can alias `default_crew_llm` to `default_llm` for now.
default_llm = default_crew_llm
if default_llm:
    print(f"llm_config.py: `default_llm` (alias for `default_crew_llm`) is ready.")
else:
    print(f"llm_config.py: `default_llm` (alias for `default_crew_llm`) is None.")
