from crewai_tools import DirectoryReadTool, FileReadTool

# Initialize DirectoryReadTool
# For demonstration, it reads from the current directory.
# In a real scenario, this might be 'src/' or a specific project path.
directory_reader_tool = DirectoryReadTool(directory='.')

# Initialize FileReadTool
# This tool can be used to read specific files by providing filepath during agent execution.
file_reader_tool = FileReadTool()

# List of knowledge tool instances to be imported by crews
knowledge_tool_list = [directory_reader_tool, file_reader_tool]
