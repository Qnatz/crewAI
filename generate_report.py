import json

def generate_dependency_report():
    core_deps_toml = [
        'appdirs', 'auth0-python', 'blinker', 'chromadb', 'click', 'instructor',
        'json-repair', 'json5', 'jsonref', 'litellm', 'onnxruntime', 'openai',
        'opentelemetry-api', 'opentelemetry-exporter-otlp-proto-http',
        'opentelemetry-sdk', 'openpyxl', 'pdfplumber', 'pydantic', 'python-dotenv',
        'pyvis', 'regex', 'tokenizers', 'tomli', 'tomli-w'
    ]

    optional_deps_toml = {
        'agentops': ['agentops'], 'aisuite': ['aisuite'], 'docling': ['docling'],
        'embeddings': ['tiktoken'], 'mem0': ['mem0ai'],
        'openpyxl_opt': ['openpyxl'], # Key changed to avoid clash in this dict if 'openpyxl' was a category name
        'pandas_opt': ['pandas'],   # Key changed
        'pdfplumber_opt': ['pdfplumber'], # Key changed
        'tools': ['crewai-tools']
    }

    # This is the JSON data from the previous successful subtask (step 3)
    import_map_json_string = '''
    {
      "pydantic": [
        "src/crewai/agent.py", "src/crewai/agents/agent_adapters/base_agent_adapter.py",
        "src/crewai/agents/agent_adapters/langgraph/langgraph_adapter.py",
        "src/crewai/agents/agent_adapters/openai_agents/openai_adapter.py",
        "src/crewai/agents/agent_builder/base_agent.py",
        "src/crewai/agents/agent_builder/utilities/base_output_converter.py",
        "src/crewai/agents/cache/cache_handler.py", "src/crewai/cli/config.py",
        "src/crewai/crew.py", "src/crewai/crews/crew_output.py", "src/crewai/flow/flow.py",
        "src/crewai/flow/flow_trackable.py", "src/crewai/flow/persistence/__init__.py",
        "src/crewai/flow/persistence/base.py", "src/crewai/flow/persistence/decorators.py",
        "src/crewai/flow/persistence/sqlite.py", "src/crewai/knowledge/knowledge.py",
        "src/crewai/knowledge/knowledge_config.py",
        "src/crewai/knowledge/source/base_file_knowledge_source.py",
        "src/crewai/knowledge/source/base_knowledge_source.py",
        "src/crewai/knowledge/source/crew_docling_source.py",
        "src/crewai/knowledge/source/excel_knowledge_source.py",
        "src/crewai/knowledge/source/string_knowledge_source.py", "src/crewai/lite_agent.py",
        "src/crewai/llm.py", "src/crewai/memory/entity/entity_memory.py",
        "src/crewai/memory/memory.py", "src/crewai/memory/short_term/short_term_memory.py",
        "src/crewai/security/fingerprint.py", "src/crewai/security/security_config.py",
        "src/crewai/task.py", "src/crewai/tasks/conditional_task.py",
        "src/crewai/tasks/guardrail_result.py", "src/crewai/tasks/llm_guardrail.py",
        "src/crewai/tasks/task_output.py", "src/crewai/tools/agent_tools/add_image_tool.py",
        "src/crewai/tools/agent_tools/ask_question_tool.py",
        "src/crewai/tools/agent_tools/base_agent_tools.py",
        "src/crewai/tools/agent_tools/delegate_work_tool.py", "src/crewai/tools/base_tool.py",
        "src/crewai/tools/cache_tools/cache_tools.py", "src/crewai/tools/structured_tool.py",
        "src/crewai/tools/tool_calling.py", "src/crewai/types/crew_chat.py",
        "src/crewai/types/usage_metrics.py", "src/crewai/utilities/config.py",
        "src/crewai/utilities/converter.py", "src/crewai/utilities/crew_json_encoder.py",
        "src/crewai/utilities/crew_pydantic_output_parser.py",
        "src/crewai/utilities/evaluators/crew_evaluator_handler.py",
        "src/crewai/utilities/evaluators/task_evaluator.py",
        "src/crewai/utilities/events/base_events.py",
        "src/crewai/utilities/events/event_listener.py",
        "src/crewai/utilities/events/flow_events.py",
        "src/crewai/utilities/events/llm_events.py", "src/crewai/utilities/i18n.py",
        "src/crewai/utilities/logger.py", "src/crewai/utilities/planning_handler.py",
        "src/crewai/utilities/prompts.py", "src/crewai/utilities/pydantic_schema_parser.py",
        "src/crewai/utilities/reasoning_handler.py", "src/crewai/utilities/rpm_controller.py",
        "src/crewai/utilities/serialization.py",
        "src/crewai/utilities/task_output_storage_handler.py"
      ],
      "crewai_tools": ["src/crewai/agent.py"],
      "dotenv": ["src/crewai/llm.py", "src/crewai/project/crew_base.py"],
      "litellm": [
        "src/crewai/llm.py", "src/crewai/utilities/internal_instructor.py",
        "src/crewai/utilities/token_counter_callback.py"
      ],
      "appdirs": ["src/crewai/utilities/paths.py"],
      "instructor": ["src/crewai/utilities/internal_instructor.py"],
      "regex": ["src/crewai/utilities/crew_pydantic_output_parser.py"],
      "chromadb": [
        "src/crewai/knowledge/storage/knowledge_storage.py",
        "src/crewai/memory/storage/rag_storage.py",
        "src/crewai/utilities/embedding_configurator.py"
      ],
      "ibm_watsonx_ai": ["src/crewai/utilities/embedding_configurator.py"],
      "rich": [
        "src/crewai/cli/authentication/main.py", "src/crewai/cli/command.py",
        "src/crewai/cli/deploy/main.py", "src/crewai/cli/organization/main.py",
        "src/crewai/cli/tools/main.py", "src/crewai/cli/utils.py",
        "src/crewai/utilities/evaluators/crew_evaluator_handler.py",
        "src/crewai/utilities/events/utils/console_formatter.py"
      ],
      "blinker": ["src/crewai/utilities/events/crewai_event_bus.py"],
      "agentops": ["src/crewai/utilities/events/third_party/agentops_listener.py"],
      "pyvis": ["src/crewai/flow/flow_visualizer.py"],
      "requests": [
        "src/crewai/cli/authentication/main.py", "src/crewai/cli/command.py",
        "src/crewai/cli/plus_api.py", "src/crewai/cli/provider.py"
      ],
      "click": [
        "src/crewai/cli/add_crew_to_flow.py", "src/crewai/cli/cli.py",
        "src/crewai/cli/create_crew.py", "src/crewai/cli/create_flow.py",
        "src/crewai/cli/crew_chat.py", "src/crewai/cli/evaluate_crew.py",
        "src/crewai/cli/install_crew.py", "src/crewai/cli/kickoff_flow.py",
        "src/crewai/cli/plot_flow.py", "src/crewai/cli/provider.py",
        "src/crewai/cli/replay_from_task.py", "src/crewai/cli/reset_memories_command.py",
        "src/crewai/cli/run_crew.py", "src/crewai/cli/tools/main.py",
        "src/crewai/cli/train_crew.py", "src/crewai/cli/utils.py"
      ],
      "tomli": ["src/crewai/cli/crew_chat.py", "src/crewai/cli/utils.py"],
      "packaging": ["src/crewai/cli/crew_chat.py", "src/crewai/cli/run_crew.py"],
      "tomli_w": ["src/crewai/cli/update_crew.py"],
      "auth0": ["src/crewai/cli/authentication/utils.py"],
      "cryptography": ["src/crewai/cli/authentication/utils.py"],
      "json5": ["src/crewai/tools/tool_usage.py"],
      "json_repair": ["src/crewai/agents/parser.py", "src/crewai/tools/tool_usage.py"],
      "yaml": ["src/crewai/project/crew_base.py"],
      "langchain_core": [
        "src/crewai/agents/agent_adapters/langgraph/langgraph_adapter.py",
        "src/crewai/agents/agent_adapters/langgraph/langgraph_tool_adapter.py"
      ],
      "langgraph": ["src/crewai/agents/agent_adapters/langgraph/langgraph_adapter.py"],
      "aisuite": ["src/crewai/llms/third_party/ai_suite.py"],
      "docling": ["src/crewai/knowledge/source/crew_docling_source.py"],
      "pandas": ["src/crewai/knowledge/source/excel_knowledge_source.py"],
      "numpy": [
        "src/crewai/knowledge/embedder/base_embedder.py",
        "src/crewai/knowledge/source/base_knowledge_source.py"
      ],
      "pdfplumber": ["src/crewai/knowledge/source/pdf_knowledge_source.py"],
      "opentelemetry": ["src/crewai/telemetry/telemetry.py"],
      "mem0": ["src/crewai/memory/storage/mem0_storage.py"]
    }
    '''
    import_map = json.loads(import_map_json_string)

    termux_problematic_high = ['onnxruntime', 'mem0ai']
    termux_problematic_potential = ['chromadb', 'tokenizers', 'tiktoken']
    termux_needs_verification = ['aisuite'] # Example, assuming aisuite needs specific checks
    termux_likely_ok_c_backed = ['regex', 'pandas', 'cryptography', 'numpy', 'yaml'] # Examples

    # Normalization map for TOML names to import names
    normalization_map = {
        "python-dotenv": "dotenv",
        "auth0-python": "auth0",
        "opentelemetry-api": "opentelemetry",
        "opentelemetry-sdk": "opentelemetry",
        "opentelemetry-exporter-otlp-proto-http": "opentelemetry",
        "json-repair": "json_repair",
        "mem0ai": "mem0",
        "crewai-tools": "crewai_tools"
        # Default for others: dep_toml itself (e.g. 'pydantic' -> 'pydantic')
    }

    # Dependencies that might be transitive or dynamically loaded, so absence in import_map isn't definitive proof of non-use
    not_directly_imported_suspects = ['openai', 'onnxruntime', 'tokenizers', 'tiktoken', 'jsonref', 'openpyxl']


    def get_termux_status(dep_name_toml, import_name_actual):
        status = "OK (Pure Python or common)"
        note = "" # Default empty note

        # Determine status based on problematic lists
        if dep_name_toml in termux_problematic_high or import_name_actual in termux_problematic_high:
            status = "**HIGHLY PROBLEMATIC**"
        elif dep_name_toml == "mem0ai" or import_name_actual == "mem0": # mem0ai maps to mem0
             status = "**HIGHLY PROBLEMATIC**"
        elif dep_name_toml in termux_problematic_potential or import_name_actual in termux_problematic_potential:
            status = "**POTENTIALLY PROBLEMATIC**"
        elif dep_name_toml in termux_needs_verification or import_name_actual in termux_needs_verification:
            status = "**NEEDS VERIFICATION**"
        elif dep_name_toml in termux_likely_ok_c_backed or import_name_actual in termux_likely_ok_c_backed:
            status = "**LIKELY OK (C-backed)**"

        # Check if the import_name_actual is found in the import_map keys
        # But exclude opentelemetry group from this specific note as it's handled as a group
        if import_name_actual not in import_map and not dep_name_toml.startswith("opentelemetry-"):
            if dep_name_toml in not_directly_imported_suspects or import_name_actual in not_directly_imported_suspects:
                note = " (Not directly found in AST import map; could be transitive, dynamically loaded, or only in non-scanned files)"
            else:
                note = " (Not found in AST import map for scanned files)"

        return f"{status}{note}"

    markdown_lines = []
    markdown_lines.append("# Dependency Analysis for Termux Compatibility")
    markdown_lines.append("\nThis report analyzes the project's dependencies, lists the files that import them, and assesses their compatibility with Termux, highlighting potentially problematic ones.\n")

    # --- Process Core Dependencies ---
    markdown_lines.append("## Core Dependencies (`pyproject.toml`)\n")
    processed_opentelemetry_group = False
    for dep_toml in sorted(list(set(core_deps_toml))): # Use set for unique processing
        if dep_toml.startswith("opentelemetry-"):
            if processed_opentelemetry_group:
                continue # Skip individual opentelemetry entries if group already processed
            import_name = "opentelemetry"
            display_name = "opentelemetry (group: opentelemetry-api, -sdk, -exporter-otlp-proto-http)"
            processed_opentelemetry_group = True
        else:
            import_name = normalization_map.get(dep_toml, dep_toml.replace("-", "_"))
            display_name = dep_toml

        termux_status = get_termux_status(dep_toml, import_name)
        markdown_lines.append(f"*   **{display_name}**")
        markdown_lines.append(f"    *   Termux Status: {termux_status}")

        files = import_map.get(import_name)
        if files:
            markdown_lines.append("    *   Imported in:")
            for f_path in sorted(list(files)): # Sort files for consistent output
                markdown_lines.append(f"        *   `{f_path}`")
        # Note for not directly imported is now part of get_termux_status
        markdown_lines.append("")

    # --- Process Optional Dependencies ---
    markdown_lines.append("\n## Optional Dependencies (`pyproject.toml`)\n")
    for category, deps in sorted(optional_deps_toml.items()):
        markdown_lines.append(f"### Category: `{category.replace('_opt', '')}`\n") # Clean up category name
        for dep_toml in sorted(deps):
            import_name = normalization_map.get(dep_toml, dep_toml.replace("-", "_"))
            display_name_opt = f"{dep_toml}"
            if dep_toml != import_name and import_name != dep_toml.replace("-","_"): # Show 'imports as' if significantly different
                 display_name_opt += f" (imports as `{import_name}`)"

            termux_status = get_termux_status(dep_toml, import_name)
            markdown_lines.append(f"*   **{display_name_opt}**")
            markdown_lines.append(f"    *   Termux Status: {termux_status}")

            files = import_map.get(import_name)
            if files:
                markdown_lines.append("    *   Imported in:")
                for f_path in sorted(list(files)):
                    markdown_lines.append(f"        *   `{f_path}`")
            markdown_lines.append("")

    # --- Process Additionally Imported Modules ---
    markdown_lines.append("\n## Additionally Imported Modules (Found in code, not direct TOML dependencies)\n")
    markdown_lines.append("These modules were imported in the codebase but are not listed as direct dependencies in `pyproject.toml`. They are likely transitive dependencies pulled in by other listed packages, or standard library modules that were not filtered out by the initial AST scan script (if any).\n")

    # Create a set of all import names derived from TOML core and optional dependencies
    all_toml_derived_import_names = set()
    for dep_toml in core_deps_toml:
        all_toml_derived_import_names.add(normalization_map.get(dep_toml, dep_toml.replace("-", "_")))
    if processed_opentelemetry_group : # Ensure 'opentelemetry' group name is included
        all_toml_derived_import_names.add("opentelemetry")

    for dep_list in optional_deps_toml.values():
        for dep_toml in dep_list:
            all_toml_derived_import_names.add(normalization_map.get(dep_toml, dep_toml.replace("-", "_")))

    # Identify modules in import_map that are not in all_toml_derived_import_names
    additionally_imported_actual = sorted(list(set(import_map.keys()) - all_toml_derived_import_names))

    for import_name in additionally_imported_actual:
        # For these, the 'package name' (dep_toml) is the same as import_name for status checking
        termux_status = get_termux_status(import_name, import_name)
        markdown_lines.append(f"*   **{import_name}**")
        markdown_lines.append(f"    *   Termux Status: {termux_status}")
        markdown_lines.append(f"    *   Note: This module is imported but not a direct TOML dependency. Likely transitive or a standard library module.")
        files = import_map.get(import_name) # Should always exist as these keys come from import_map
        if files: # Redundant check but safe
            markdown_lines.append("    *   Imported in:")
            for f_path in sorted(list(files)):
                markdown_lines.append(f"        *   `{f_path}`")
        markdown_lines.append("")

    with open("dependency_analysis.md", "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    return "Successfully generated dependency_analysis.md"

if __name__ == "__main__":
    report_status = generate_dependency_report()
    print(report_status)
