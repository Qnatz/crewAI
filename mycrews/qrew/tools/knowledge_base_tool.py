from crewai.tools import BaseTool # Use BaseTool for CrewAI tool compatibility
from typing import Union, Any # Added for type hinting

class KnowledgeBaseTool(BaseTool):
    name: str = "Knowledge Base Query Tool"
    description: str = (
        "A tool to query the project's knowledge base for information, "
        "context, or answers to specific questions. Useful for understanding "
        "project history, technical decisions, or existing functionalities."
    )

    def _run(self, question: Union[str, dict, Any]) -> str: # Changed type hint
        actual_question_text = ""
        if isinstance(question, str):
            actual_question_text = question
        elif isinstance(question, dict):
            if "question" in question and isinstance(question.get("question"), dict) and "description" in question.get("question", {}):
                actual_question_text = question["question"]["description"]
            elif "description" in question: # Matches the structure from the error
                actual_question_text = question["description"]
            else:
                actual_question_text = f"Error: Received a dictionary but could not extract question. Input: {str(question)}"
        else:
            actual_question_text = f"Error: Unexpected input type for question. Input: {str(question)}"

        # Placeholder implementation
        # In the future, this will interact with the .tflite embedding model
        # and a vector store or similar mechanism to retrieve relevant information.
        print(f"KnowledgeBaseTool received query: '{actual_question_text}'")
        dummy_response = (
            f"Response for '{actual_question_text}': Information retrieved from knowledge base. "
            "(Note: .tflite model not yet integrated. This is a placeholder response.)"
        )
        return dummy_response

    # If you need an async version, you can implement _arun
    # async def _arun(self, question: Union[str, dict, Any]) -> str: # Type hint could also be updated here
    #     # Placeholder async implementation
    #     # Similar logic for extracting actual_question_text would be needed here
    #     actual_question_text = "" # Simplified for brevity, but should mirror _run's logic
    #     if isinstance(question, str):
    #         actual_question_text = question
    #     elif isinstance(question, dict):
    #         if "question" in question and isinstance(question.get("question"), dict) and "description" in question.get("question", {}):
    #             actual_question_text = question["question"]["description"]
    #         elif "description" in question:
    #             actual_question_text = question["description"]
    #         else:
    #             actual_question_text = f"Error: Async: Received a dictionary but could not extract question. Input: {str(question)}"
    #     else:
    #         actual_question_text = f"Error: Async: Unexpected input type for question. Input: {str(question)}"

    #     print(f"KnowledgeBaseTool (async) received query: '{actual_question_text}'")
    #     dummy_response = (
    #         f"Async response for '{actual_question_text}': Information retrieved from knowledge base. "
    #         "(Note: .tflite model not yet integrated. This is a placeholder response.)"
    #     )
    #     return dummy_response

# To make it directly usable, you might instantiate it or provide a function to get an instance
knowledge_base_tool_instance = KnowledgeBaseTool()

# Example of how an agent might use it (conceptual):
# from crewAI.qrew.tools.knowledge_base_tool import knowledge_base_tool_instance
# agent_tools = [knowledge_base_tool_instance]
