# tools/inbuilt_tools.py
# Description: A collection of pre-instantiated CrewAI tools for common agent tasks,
# especially useful for code generation, research, and file system interaction.

# It's assumed that 'crewai_tools' is installed and these tools are available.
# For tools requiring API keys (e.g., GithubSearchTool, SerperDevTool, ExaSearchTool),
# it's expected that the necessary environment variables (e.g., GITHUB_API_KEY,
# SERPER_API_KEY, EXA_API_KEY) will be set in the environment where the agents run.

from crewai_tools import (
    CodeInterpreterTool,
    FileReadTool,
    FileWriteTool,
    CodeDocsSearchTool,
    GithubSearchTool,
    DirectoryReadTool,
    DirectorySearchTool,
    TXTSearchTool,
    PDFSearchTool,
    MDXSearchTool,
    ExaSearchTool,
    WebsiteSearchTool,
    SerperDevTool
    # RagTool # Example if we needed it, but not in the primary list for now
)

# --- Code Execution & File System Tools ---
# For interpreting/executing code and interacting with files/directories.

# CodeInterpreterTool: Interprets and executes Python code.
# Useful for generating, running, and validating code snippets.
code_interpreter_tool = CodeInterpreterTool()

# FileReadTool: Reads the content of a specific file.
file_read_tool = FileReadTool()

# FileWriteTool: Writes content to a specific file.
# Can be used to save generated code, test results, or other artifacts.
# Takes file_path and text content as input.
file_write_tool = FileWriteTool()

# DirectoryReadTool: Reads and lists the contents of a specified directory.
# Helpful for understanding project structure.
directory_read_tool = DirectoryReadTool()

# DirectorySearchTool: Searches for files/directories within a specified path.
# Can use patterns or specific names.
directory_search_tool = DirectorySearchTool()


# --- Documentation, Code Reference & Local Content Search Tools ---
# For searching within code, documentation, and various local file types.

# CodeDocsSearchTool: Semantic search through language documentation (e.g., Python, JavaScript).
# Requires specifying the documentation to search (e.g., search_tool.docs_search("python", "how to use lists"))
# May require pre-loading or configuration of documentation sources depending on implementation.
# For now, instantiated with defaults. User might need to configure with specific docs.
code_docs_search_tool = CodeDocsSearchTool()

# GithubSearchTool: Searches GitHub repositories for code, issues, etc.
# Requires GITHUB_API_KEY environment variable.
github_search_tool = GithubSearchTool()

# TXTSearchTool: Searches within plain text files.
# Useful for specific information in .txt files.
# Often takes a directory path and a search query.
txt_search_tool = TXTSearchTool() # Assuming it can search within a given text file or directory of txt files.
                                  # Or, if it's for a single file, FileReadTool + string search might be an alternative.
                                  # The crewai_tools version is typically for searching content within a specified .txt file.

# PDFSearchTool: Searches for text content within PDF files.
pdf_search_tool = PDFSearchTool()

# MDXSearchTool: Searches within MDX (Markdown with JSX) files.
mdx_search_tool = MDXSearchTool()


# --- External Data Lookup & Web Search Tools ---
# For fetching up-to-date information, examples, or dependencies from the web.

# SerperDevTool: Uses Serper.dev for Google search results.
# Requires SERPER_API_KEY environment variable.
serper_dev_tool = SerperDevTool()

# WebsiteSearchTool: Searches content on specific websites.
# Usually requires a website URL and a search query.
# Default implementation in crewai_tools uses requests/BeautifulSoup, generally Termux-friendly.
website_search_tool = WebsiteSearchTool()

# ExaSearchTool: Uses Exa (formerly Metaphor) for neural search.
# Requires EXA_API_KEY environment variable.
exa_search_tool = ExaSearchTool()


# Example of how these might be grouped for an agent, though not done here:
# all_inbuilt_tools = [
# code_interpreter_tool,
# file_read_tool,
# file_write_tool,
# directory_read_tool,
# directory_search_tool,
# code_docs_search_tool,
# github_search_tool,
# txt_search_tool,
# pdf_search_tool,
# mdx_search_tool,
# serper_dev_tool,
# website_search_tool,
# exa_search_tool,
# ]

# For more specific tool configurations (e.g., FileWriteTool with a root_dir,
# or search tools with specific knowledge bases), they can be instantiated separately
# by the agent or crew setup logic. This file provides the basic, default instances.
