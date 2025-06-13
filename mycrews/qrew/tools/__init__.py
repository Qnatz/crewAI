from .knowledge_base_tool import KnowledgeBaseTool
from tools.objectbox_memory import ObjectBoxMemory
from .shell_tool import shell_tool

memory = ObjectBoxMemory()
knowledge_base_tool_instance = KnowledgeBaseTool(memory_instance=memory)

__all__ = [
    'KnowledgeBaseTool',
    'knowledge_base_tool_instance',
    'ShellTool'
]
