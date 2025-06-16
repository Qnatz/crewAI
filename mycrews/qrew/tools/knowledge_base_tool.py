from crewai.tools import BaseTool
from typing import Union, Any, Optional
from .onnx_objectbox_memory import ONNXObjectBoxMemory # Changed import
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store ONNX embedding model initialization status
ONNX_EMBEDDING_INITIALIZATION_STATUS = [("ONNX Embedding Model", False)]

class KnowledgeBaseTool(BaseTool): # Renamed from EnhancedKnowledgeBaseTool
    name: str = "Enhanced Knowledge Base Tool" # Name from the new tool
    description: str = (
        "A comprehensive knowledge base system that combines semantic search with LLM reasoning. "
        "First retrieves relevant context using embeddings, then generates answers using an LLM. "
        "Input can be a simple string question or a dictionary with: "
        "{'question': 'your question', 'llm': llm_instance, 'max_context': 5}"
    )
    memory_instance: Optional[ONNXObjectBoxMemory] = None # Changed type hint
    embedding_session: Optional[ort.InferenceSession] = None
    tokenizer: Optional[Tokenizer] = None

    def __init__(
        self,
        memory_instance: Optional[ONNXObjectBoxMemory] = None, # Changed type hint
        onnx_model_path: str = "models/onnx/model.onnx", # Default path from new tool
        tokenizer_path: str = "models/onnx/tokenizer.json", # Default path from new tool
        **kwargs
    ):
        super().__init__(**kwargs)
        self.memory_instance = memory_instance or ONNXObjectBoxMemory() # Changed instantiation

        # Initialize embedding model
        try:
            options = ort.SessionOptions()
            options.intra_op_num_threads = os.cpu_count() or 1
            self.embedding_session = ort.InferenceSession(onnx_model_path, options)
            self.tokenizer = Tokenizer.from_file(tokenizer_path)
            logger.info("Embedding model loaded successfully")
            ONNX_EMBEDDING_INITIALIZATION_STATUS[0] = ("ONNX Embedding Model", True)
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            self.embedding_session = None
            self.tokenizer = None

    def _embed_text(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text using ONNX model"""
        if not self.tokenizer or not self.embedding_session:
            logger.warning("Tokenizer or embedding session not available for embedding text.")
            return None

        try:
            encoded = self.tokenizer.encode(text)
            inputs = {
                "input_ids": np.array([encoded.ids], dtype=np.int64),
                "attention_mask": np.array([encoded.attention_mask], dtype=np.int64),
                "token_type_ids": np.array([encoded.type_ids], dtype=np.int64)
            }
            token_embeddings = self.embedding_session.run(None, inputs)[0][0]
            return np.mean(token_embeddings, axis=0).astype(np.float32)
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return None

    def _run(self, input_data: Union[str, dict, Any]) -> str:
        # Parse input
        question = ""
        llm = None
        max_context = 3

        if isinstance(input_data, str):
            question = input_data
        elif isinstance(input_data, dict):
            question = input_data.get("question", input_data.get("description", ""))
            llm = input_data.get("llm")
            max_context = input_data.get("max_context", 3)
        else:
            return "Error: Invalid input format. Please provide a string or dictionary with 'question' key"

        if not question:
            return "Error: No question provided"

        logger.info(f"Knowledge query: {question}")

        # Retrieve context using embeddings
        try:
            if self.embedding_session and self.tokenizer: # Make sure tokenizer is also available
                query_embedding = self._embed_text(question)
                if query_embedding is not None:
                    logger.info("Successfully generated query embedding.")
                    context_results = self.memory_instance.vector_query(
                        query_vector=query_embedding, # Pass ndarray directly
                        limit=max_context
                    )
                else:
                    logger.warning("Embedding generation failed. Cannot perform vector search without query embedding.")
                    return "Embedding generation failed, cannot perform search." # Changed message
            else:
                logger.warning("Embedding session/tokenizer not available. Cannot perform vector search.")
                return "Embedding session/tokenizer not available, cannot perform search." # Changed message

            if not context_results:
                return "No relevant information found in the knowledge base."

            context_str = "\n\n".join([f"• {res['content']}" for res in context_results])
            logger.info(f"Retrieved {len(context_results)} context items")
        except Exception as e:
            logger.error(f"Knowledge retrieval error: {str(e)}")
            return f"Knowledge retrieval error: {str(e)}"

        # Generate answer with LLM if available
        if llm:
            try:
                prompt = f"""
                You are an expert knowledge assistant. Use the provided context to answer the user's question.
                If the context doesn't contain the answer, say you don't know. Don't generate false information.

                Context:
                {context_str}

                Question: {question}

                Answer:
                """
                # Assuming llm object has a 'generate' or similar method
                # This part might need adjustment based on the actual LLM interface in crewAI
                if hasattr(llm, 'generate'):
                    return llm.generate(prompt)
                elif hasattr(llm, 'invoke'): # Common in Langchain
                    return llm.invoke(prompt)
                elif hasattr(llm, 'chat'): # Another common interface
                    return llm.chat(prompt)
                else:
                    logger.error("LLM object does not have a recognized generation method (e.g., generate, invoke, chat).")
                    return f"LLM interface error. Relevant context:\n\n{context_str}"

            except Exception as e:
                logger.error(f"LLM generation error: {str(e)}")
                return f"LLM generation error: {str(e)}\n\nRelevant context:\n{context_str}"

        # Fallback to returning context if no LLM provided
        return f"Relevant knowledge context:\n\n{context_str}"

    async def _arun(self, input_data: Union[str, dict, Any]) -> str:
        # Basic async wrapper, consider true async implementation if I/O bound
        logger.info("Async _arun called, currently wraps sync _run. For true async, implement I/O calls with await.")
        return self._run(input_data) # Consider using asyncio.to_thread for CPU bound sync code in async

# Instantiation for mycrews/qrew/tools/__init__.py to pick up
knowledge_base_tool_instance = KnowledgeBaseTool(
    onnx_model_path="models/onnx/model.onnx",
    tokenizer_path="models/onnx/tokenizer.json"
)
