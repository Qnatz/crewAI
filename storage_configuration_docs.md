# Configuring Vector Storage Backends

CrewAI now supports swappable vector storage backends for its Knowledge Base and Agent Memory systems (specifically for components that use RAG, like ShortTermMemory and EntityMemory). This allows for greater flexibility, especially in environments where installing certain dependencies (like those required by ChromaDB) might be challenging (e.g., Termux).

## Key Configuration Dictionary: `storage_config`

The primary way to configure a vector store is through a `storage_config` dictionary. This dictionary is passed to classes like `Knowledge` (for knowledge bases), or to memory classes like `ShortTermMemory` and `EntityMemory` (usually via the `Agent` and `Crew` configurations).

The basic structure of `storage_config` is:

```python
storage_config = {
    "type": "backend_name",  # "chromadb" or "sqlite"
    "collection_name": "my_specific_collection", # Name for the DB table or Chroma collection
    "persist_path": "/path/to/your/storage_location", # Optional: directory for persistence
    # ... other backend-specific options ...
}
```

-   **`type`**: (Required) A string specifying the backend to use.
    -   `"chromadb"`: Uses `ChromaDBVectorStore`. This is often the default if no `storage_config` is provided.
    -   `"sqlite"`: Uses `SQLiteVectorStore`, which is a more lightweight option using SQLite and NumPy for vector operations.
-   **`collection_name`**: (Required within the config passed to the store, often defaulted by higher-level classes) The name for the specific database table (for SQLite) or collection (for ChromaDB). Higher-level classes like `Knowledge`, `ShortTermMemory`, or `EntityMemory` usually derive a sensible default for this based on their context (e.g., knowledge base name, memory type, agent ID).
-   **`persist_path`**: (Optional) The file system directory where the vector store should persist its data.
    -   If not provided, a default path is used (e.g., within a `.crewai` directory in the user's home, or `./storage` relative to the project, under subdirectories like `knowledge_stores`, `memory/entities`, `memory/short_term`).
    -   For `SQLiteVectorStore`, this will be the directory where the `[collection_name].db` file is stored.
    -   For `ChromaDBVectorStore`, this will be the root directory for ChromaDB's persistent storage.

## Hierarchical Configuration

Configuration for vector storage and embedders can be set at multiple levels, allowing for global defaults and specific overrides:

1.  **Crew Level:**
    -   `Crew(..., embedder_config={...}, default_kb_storage_config={...}, default_memory_storage_config={...})`
    -   `embedder_config`: Sets the default embedding model configuration for all components within the crew (knowledge bases, memories) unless overridden at a lower level.
    -   `default_kb_storage_config`: Sets the default `storage_config` for any `Knowledge` instances created by the crew (e.g., the crew's main knowledge base if `knowledge_sources` are provided at crew initialization).
    -   `default_memory_storage_config`: Sets the default `storage_config` for memory systems (`ShortTermMemory`, `EntityMemory`) initialized by the crew for its agents.

2.  **Agent Level:**
    -   `Agent(..., embedder={...}, kb_storage_config={...}, kb_embedder_config={...}, memory_storage_config={...}, memory_embedder_config={...})`
    -   `embedder`: Agent's default embedder, overrides crew's `embedder_config` for this agent.
    -   `kb_storage_config` & `kb_embedder_config`: Specific configurations for the agent's own knowledge base (if it has one, typically set up via `agent.set_knowledge()`). These override any crew defaults for this agent's KB.
    -   `memory_storage_config` & `memory_embedder_config`: Specific configurations for this agent's memory components. These are stored on the agent and used by `ContextualMemory` (when initialized by `Crew`) to set up the agent's `ShortTermMemory` and `EntityMemory`.

3.  **Knowledge Class Level:**
    -   `Knowledge(collection_name="my_kb", sources=[...], storage_config={...}, embedder_config={...})`
    -   Directly configures the storage and embedder for a specific `Knowledge` instance, overriding any agent or crew defaults.

## Examples

### Configuring `ChromaDBVectorStore` (Default)

ChromaDB is typically the default if no `storage_config` is specified, or if explicitly set.

```python
from crewai import Crew, Agent, Knowledge
from crewai.utilities.paths import db_storage_path # Helper for default paths

# Example: Crew-level default to ChromaDB for all KBs and Memories
# db_storage_path() provides a sensible default like ~/.crewai/project_name/
crew_default_chroma_kb_storage = {
    "type": "chromadb",
    "persist_path": str(db_storage_path() / "crew_default_kb_chroma")
    # collection_name will be defaulted by Knowledge/Agent classes
}
crew_default_chroma_mem_storage = {
    "type": "chromadb",
    "persist_path": str(db_storage_path() / "crew_default_mem_chroma")
}
# Define a global embedder config
default_embedder_cfg = {"provider": "openai", "config": {"model": "text-embedding-3-small"}}


my_crew = Crew(
    # ... other crew params ...
    embedder_config=default_embedder_cfg,
    default_kb_storage_config=crew_default_chroma_kb_storage,
    default_memory_storage_config=crew_default_chroma_mem_storage
)

# Agent-specific ChromaDB config for its KnowledgeBase (if it creates one)
# This agent will use the crew's default embedder_config
agent_kb_storage = {
    "type": "chromadb",
    "collection_name": "researcher_agent_kb", # Explicit collection name
    "persist_path": str(db_storage_path() / "agents" / "researcher_kb_chroma")
}
researcher = Agent(
    role="Researcher",
    # ... other agent params ...
    kb_storage_config=agent_kb_storage
    # embedder_config could also be set here to override crew's default for this agent's KB
)
```

### Configuring `SQLiteVectorStore` (for Termux or lightweight needs)

This is useful when `chromadb`'s dependencies are hard to install or a lighter solution is preferred.

```python
from crewai import Crew, Agent
from crewai.utilities.paths import db_storage_path

# Define your embedder config (mandatory for SQLiteVectorStore to generate embeddings)
# Ensure OPENAI_API_KEY is set in your environment if using OpenAI
openai_embedder_cfg = {"provider": "openai", "config": {"model": "text-embedding-3-small"}}
# For local models not needing ONNX, e.g., from sentence-transformers via LiteLLM:
# local_embedder_cfg = {"provider": "litellm", "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"}}


# Example: Crew-level default to SQLite for all KBs and Memories
crew_default_sqlite_kb_storage = {
    "type": "sqlite",
    "persist_path": str(db_storage_path() / "crew_default_kb_sqlite")
    # collection_name will be defaulted by Knowledge/Agent classes
}
crew_default_sqlite_mem_storage = {
    "type": "sqlite",
    "persist_path": str(db_storage_path() / "crew_default_mem_sqlite")
}

my_crew = Crew(
    # ... other crew params ...
    embedder_config=openai_embedder_cfg, # Global embedder for the crew
    default_kb_storage_config=crew_default_sqlite_kb_storage,
    default_memory_storage_config=crew_default_sqlite_mem_storage
)

# Agent-specific SQLite config for its memory system
# This agent will use the crew's default openai_embedder_cfg for its memory
agent_mem_sqlite = {
    "type": "sqlite",
    "collection_name": "planner_agent_memory", # Explicit collection name
    "persist_path": str(db_storage_path() / "agents" / "planner_agent_mem_sqlite")
}
planner_agent = Agent(
    role="Planner",
    # ... other agent params ...
    memory_storage_config=agent_mem_sqlite
    # memory_embedder_config can be set here to override crew's default for this agent's memory
)
```

## `embedder_config`

The `embedder_config` dictionary is crucial as it defines how text is converted into vectors. It's used by both `ChromaDBVectorStore` (passed as `embedding_function` to ChromaDB) and `SQLiteVectorStore` (used to explicitly generate embeddings before storage/search). The structure of `embedder_config` is typically:

```python
embedder_config = {
    "provider": "provider_name",  # e.g., "openai", "ollama", "litellm" (for local sentence-transformers)
    "config": {
        "model": "model_name",    # e.g., "text-embedding-3-small", "nomic-embed-text", "sentence-transformers/all-MiniLM-L6-v2"
        # ... other provider-specific keys like api_key, base_url, etc.
    }
}
```
Refer to `EmbeddingConfigurator` and specific embedding provider documentation for details on available options.

## Note on `onnxruntime` for Termux Users

Users in environments like Termux where `onnxruntime` (a dependency for some local embedding models) is difficult to install should be cautious. When selecting an embedding model via `embedder_config` (especially when using `litellm` as a provider for local models), ensure the chosen model does not transitively depend on `onnxruntime`.

While `crewai`'s vector stores now have improved error handling to catch issues if an embedding model fails to load or generate embeddings (e.g., due to a missing `onnxruntime`), the underlying embedding generation will still fail if such a model is selected without its required heavy dependencies. Standard cloud-based embedding providers like OpenAI do not require `onnxruntime`.

## Default Behavior

If no `storage_config` is provided at any level (Crew, Agent, or Knowledge class), `crewai` components that require vector storage (like `KnowledgeStorage`, `RAGStorage`) will typically default to using `ChromaDBVectorStore`. The persistence path will also default to a standard location (often in a `.crewai` directory in the user's home folder or a local `./storage` directory, under subfolders like `knowledge_stores` or `memory`). Collection names will be auto-generated based on context (e.g., "crew_knowledge", "entities_default", "short_term_default").

It's recommended to explicitly configure storage for clarity and control, especially for production or persistent use cases.
