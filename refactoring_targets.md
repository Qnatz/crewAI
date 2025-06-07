# Refactoring Targets for Termux Compatibility (crewAI)

This report identifies dependencies that are reportedly not installable in the user's Termux environment and the `crewai` project files that use them. This is based on the `dependency_analysis.md` and user-provided information.

## 1. `chromadb`

- **Status:** User Confirmed: Not Installed - Candidate for Refactor
- **Reason for Original Flagging:** Uses `hnswlib` (C++ native library) and can have specific `sqlite3` version requirements, making it hard to install on Termux.
- **User's Suggested Alternative:** `sqlite3` (Note: `sqlite3` is a key-value store, `chromadb` is a vector database. A direct replacement for all of `chromadb`'s functionality with only `sqlite3` might be complex, especially for vector search capabilities. `sqlite3` could potentially replace the storage aspect if vector search is handled differently or removed).
- **`crewai` Files Importing `chromadb`:**
    - `src/crewai/knowledge/storage/knowledge_storage.py`
    - `src/crewai/memory/storage/rag_storage.py`
    - `src/crewai/utilities/embedding_configurator.py`


## 2. `onnxruntime`

- **Status:** User Confirmed: Not Installed - Candidate for Refactor
- **Reason for Original Flagging:** C++ based, large, and complex to compile/install on Termux.
- **User's Suggested Alternative:** None specified by user for this one.
- **`crewai` Files Importing `onnxruntime`:**
    - No direct imports of `onnxruntime` were found in the `src/crewai` Python files during the AST scan.
    - However, `onnxruntime` is listed as a **core dependency** in `crewai`'s `pyproject.toml`.
    - **Implication:** `onnxruntime` is likely used indirectly (e.g., called by another library that `crewai` imports) or dynamically loaded. Pinpointing specific files for refactoring requires a deeper audit of `crewai`'s features that might involve ONNX model inferencing. Any such feature would be a candidate for refactoring or removal if `onnxruntime` is unavailable.


## Notes on Other Dependencies

The following dependencies were initially flagged as potentially problematic but are **confirmed to be installed** in the user's environment (often as sub-dependencies of `litellm` which `crewai` uses):

- **`tokenizers`**: User Confirmed: Installed. (Required by `litellm`)
- **`tiktoken`**: User Confirmed: Installed. (Required by `litellm`)


The dependency `mem0ai` (which imports as `mem0`) was initially flagged as highly problematic due to its reliance on `llama-cpp-python`. Since the user has **`llama_cpp_python` installed**, features in `crewai` relying on `mem0` (e.g., `src/crewai/memory/storage/mem0_storage.py`) should be viable.

## General Approaches for Refactoring (Further details in next steps)

When a critical dependency is not available, consider these general strategies for the identified files/features:

1.  **Conditional Import & Graceful Degradation:** If the feature is non-essential, wrap its usage in `try-except ImportError` blocks. The application can then run without the feature, possibly warning the user.
2.  **Abstraction Layer:** If the functionality is essential, hide the specific library behind an abstraction layer (e.g., a base class or a set of functions). You can then create different implementations of this layer – one using the problematic library, and another using an alternative (like `sqlite3` for some `chromadb` use cases, or a different model inference method if `onnxruntime` is out).
3.  **Library Replacement:** Find a Termux-compatible library that offers similar functionality.
4.  **Feature Removal:** If the feature is not critical and alternatives are too complex, consider removing it for the Termux-specific version or build.
5.  **Stubbing Functionality:** For features where an alternative is hard, provide a stub that informs the user the feature is unavailable on Termux, rather than letting the application crash.