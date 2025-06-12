# Dependency Analysis for Termux Compatibility

This report analyzes the project's dependencies, lists the files that import them, and assesses their compatibility with Termux, highlighting potentially problematic ones.

## Core Dependencies (`pyproject.toml`)

*   **appdirs**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/utilities/paths.py`

*   **auth0-python**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/cli/authentication/utils.py`

*   **blinker**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/utilities/events/crewai_event_bus.py`

*   **chromadb**
    *   Termux Status: **POTENTIALLY PROBLEMATIC**
    *   Imported in:
        *   `src/crewai/knowledge/storage/knowledge_storage.py`
        *   `src/crewai/memory/storage/rag_storage.py`
        *   `src/crewai/utilities/embedding_configurator.py`

*   **click**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/cli/add_crew_to_flow.py`
        *   `src/crewai/cli/cli.py`
        *   `src/crewai/cli/create_crew.py`
        *   `src/crewai/cli/create_flow.py`
        *   `src/crewai/cli/crew_chat.py`
        *   `src/crewai/cli/evaluate_crew.py`
        *   `src/crewai/cli/install_crew.py`
        *   `src/crewai/cli/kickoff_flow.py`
        *   `src/crewai/cli/plot_flow.py`
        *   `src/crewai/cli/provider.py`
        *   `src/crewai/cli/replay_from_task.py`
        *   `src/crewai/cli/reset_memories_command.py`
        *   `src/crewai/cli/run_crew.py`
        *   `src/crewai/cli/tools/main.py`
        *   `src/crewai/cli/train_crew.py`
        *   `src/crewai/cli/utils.py`

*   **instructor**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/utilities/internal_instructor.py`

*   **json-repair**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/agents/parser.py`
        *   `src/crewai/tools/tool_usage.py`

*   **json5**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/tools/tool_usage.py`

*   **jsonref**
    *   Termux Status: OK (Pure Python or common) (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)

*   **litellm**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/llm.py`
        *   `src/crewai/utilities/internal_instructor.py`
        *   `src/crewai/utilities/token_counter_callback.py`

*   **onnxruntime**
    *   Termux Status: **HIGHLY PROBLEMATIC** (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)

*   **openai**
    *   Termux Status: OK (Pure Python or common) (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)

*   **openpyxl**
    *   Termux Status: OK (Pure Python or common) (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)

*   **opentelemetry (group: opentelemetry-api, -sdk, -exporter-otlp-proto-http)**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/telemetry/telemetry.py`

*   **pdfplumber**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/knowledge/source/pdf_knowledge_source.py`

*   **pydantic**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/agent.py`
        *   `src/crewai/agents/agent_adapters/base_agent_adapter.py`
        *   `src/crewai/agents/agent_adapters/langgraph/langgraph_adapter.py`
        *   `src/crewai/agents/agent_adapters/openai_agents/openai_adapter.py`
        *   `src/crewai/agents/agent_builder/base_agent.py`
        *   `src/crewai/agents/agent_builder/utilities/base_output_converter.py`
        *   `src/crewai/agents/cache/cache_handler.py`
        *   `src/crewai/cli/config.py`
        *   `src/crewai/crew.py`
        *   `src/crewai/crews/crew_output.py`
        *   `src/crewai/flow/flow.py`
        *   `src/crewai/flow/flow_trackable.py`
        *   `src/crewai/flow/persistence/__init__.py`
        *   `src/crewai/flow/persistence/base.py`
        *   `src/crewai/flow/persistence/decorators.py`
        *   `src/crewai/flow/persistence/sqlite.py`
        *   `src/crewai/knowledge/knowledge.py`
        *   `src/crewai/knowledge/knowledge_config.py`
        *   `src/crewai/knowledge/source/base_file_knowledge_source.py`
        *   `src/crewai/knowledge/source/base_knowledge_source.py`
        *   `src/crewai/knowledge/source/crew_docling_source.py`
        *   `src/crewai/knowledge/source/excel_knowledge_source.py`
        *   `src/crewai/knowledge/source/string_knowledge_source.py`
        *   `src/crewai/lite_agent.py`
        *   `src/crewai/llm.py`
        *   `src/crewai/memory/entity/entity_memory.py`
        *   `src/crewai/memory/memory.py`
        *   `src/crewai/memory/short_term/short_term_memory.py`
        *   `src/crewai/security/fingerprint.py`
        *   `src/crewai/security/security_config.py`
        *   `src/crewai/task.py`
        *   `src/crewai/tasks/conditional_task.py`
        *   `src/crewai/tasks/guardrail_result.py`
        *   `src/crewai/tasks/llm_guardrail.py`
        *   `src/crewai/tasks/task_output.py`
        *   `src/crewai/tools/agent_tools/add_image_tool.py`
        *   `src/crewai/tools/agent_tools/ask_question_tool.py`
        *   `src/crewai/tools/agent_tools/base_agent_tools.py`
        *   `src/crewai/tools/agent_tools/delegate_work_tool.py`
        *   `src/crewai/tools/base_tool.py`
        *   `src/crewai/tools/cache_tools/cache_tools.py`
        *   `src/crewai/tools/structured_tool.py`
        *   `src/crewai/tools/tool_calling.py`
        *   `src/crewai/types/crew_chat.py`
        *   `src/crewai/types/usage_metrics.py`
        *   `src/crewai/utilities/config.py`
        *   `src/crewai/utilities/converter.py`
        *   `src/crewai/utilities/crew_json_encoder.py`
        *   `src/crewai/utilities/crew_pydantic_output_parser.py`
        *   `src/crewai/utilities/evaluators/crew_evaluator_handler.py`
        *   `src/crewai/utilities/evaluators/task_evaluator.py`
        *   `src/crewai/utilities/events/base_events.py`
        *   `src/crewai/utilities/events/event_listener.py`
        *   `src/crewai/utilities/events/flow_events.py`
        *   `src/crewai/utilities/events/llm_events.py`
        *   `src/crewai/utilities/i18n.py`
        *   `src/crewai/utilities/logger.py`
        *   `src/crewai/utilities/planning_handler.py`
        *   `src/crewai/utilities/prompts.py`
        *   `src/crewai/utilities/pydantic_schema_parser.py`
        *   `src/crewai/utilities/reasoning_handler.py`
        *   `src/crewai/utilities/rpm_controller.py`
        *   `src/crewai/utilities/serialization.py`
        *   `src/crewai/utilities/task_output_storage_handler.py`

*   **python-dotenv**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/llm.py`
        *   `src/crewai/project/crew_base.py`

*   **pyvis**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/flow/flow_visualizer.py`

*   **regex**
    *   Termux Status: **LIKELY OK (C-backed)**
    *   Imported in:
        *   `src/crewai/utilities/crew_pydantic_output_parser.py`

*   **tokenizers**
    *   Termux Status: **POTENTIALLY PROBLEMATIC** (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)

*   **tomli**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/cli/crew_chat.py`
        *   `src/crewai/cli/utils.py`

*   **tomli-w**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/cli/update_crew.py`


## Optional Dependencies (`pyproject.toml`)

### Category: `agentops`

*   **agentops**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/utilities/events/third_party/agentops_listener.py`

### Category: `aisuite`

*   **aisuite**
    *   Termux Status: **NEEDS VERIFICATION**
    *   Imported in:
        *   `src/crewai/llms/third_party/ai_suite.py`

### Category: `docling`

*   **docling**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/knowledge/source/crew_docling_source.py`

### Category: `embeddings`

*   **tiktoken**
    *   Termux Status: **POTENTIALLY PROBLEMATIC** (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)

### Category: `mem0`

*   **mem0ai (imports as `mem0`)**
    *   Termux Status: **HIGHLY PROBLEMATIC**
    *   Imported in:
        *   `src/crewai/memory/storage/mem0_storage.py`

### Category: `openpyxl`

*   **openpyxl**
    *   Termux Status: OK (Pure Python or common) (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)

### Category: `pandas`

*   **pandas**
    *   Termux Status: **LIKELY OK (C-backed)**
    *   Imported in:
        *   `src/crewai/knowledge/source/excel_knowledge_source.py`

### Category: `pdfplumber`

*   **pdfplumber**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/knowledge/source/pdf_knowledge_source.py`

### Category: `tools`

*   **crewai-tools**
    *   Termux Status: OK (Pure Python or common)
    *   Imported in:
        *   `src/crewai/agent.py`


## Additionally Imported Modules (Found in code, not direct TOML dependencies)

These modules were imported in the codebase but are not listed as direct dependencies in `pyproject.toml`. They are likely transitive dependencies pulled in by other listed packages, or standard library modules that were not filtered out by the initial AST scan script (if any).

*   **cryptography**
    *   Termux Status: **LIKELY OK (C-backed)**
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/cli/authentication/utils.py`

*   **ibm_watsonx_ai**
    *   Termux Status: OK (Pure Python or common)
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/utilities/embedding_configurator.py`

*   **langchain_core**
    *   Termux Status: OK (Pure Python or common)
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/agents/agent_adapters/langgraph/langgraph_adapter.py`
        *   `src/crewai/agents/agent_adapters/langgraph/langgraph_tool_adapter.py`

*   **langgraph**
    *   Termux Status: OK (Pure Python or common)
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/agents/agent_adapters/langgraph/langgraph_adapter.py`

*   **numpy**
    *   Termux Status: **LIKELY OK (C-backed)**
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/knowledge/embedder/base_embedder.py`
        *   `src/crewai/knowledge/source/base_knowledge_source.py`

*   **packaging**
    *   Termux Status: OK (Pure Python or common)
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/cli/crew_chat.py`
        *   `src/crewai/cli/run_crew.py`

*   **requests**
    *   Termux Status: OK (Pure Python or common)
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/cli/authentication/main.py`
        *   `src/crewai/cli/command.py`
        *   `src/crewai/cli/plus_api.py`
        *   `src/crewai/cli/provider.py`

*   **rich**
    *   Termux Status: OK (Pure Python or common)
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/cli/authentication/main.py`
        *   `src/crewai/cli/command.py`
        *   `src/crewai/cli/deploy/main.py`
        *   `src/crewai/cli/organization/main.py`
        *   `src/crewai/cli/tools/main.py`
        *   `src/crewai/cli/utils.py`
        *   `src/crewai/utilities/evaluators/crew_evaluator_handler.py`
        *   `src/crewai/utilities/events/utils/console_formatter.py`

*   **yaml**
    *   Termux Status: **LIKELY OK (C-backed)**
    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.
    *   Imported in:
        *   `src/crewai/project/crew_base.py`
