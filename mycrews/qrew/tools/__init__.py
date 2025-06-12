from .knowledge_base_tool import KnowledgeBaseTool
from .objectbox_memory import ObjectBoxMemory
from .shell_tool import ShellTool

memory = ObjectBoxMemory()
knowledge_base_tool_instance = KnowledgeBaseTool(memory_instance=memory)

__all__ = [
    'KnowledgeBaseTool',
    'knowledge_base_tool_instance',
    'ShellTool'
]
