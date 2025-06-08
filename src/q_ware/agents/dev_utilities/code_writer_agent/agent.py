from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

code_writer_agent = Agent(
    role="Production Code Writer",
    goal="Generate high-quality, production-ready code in various languages and frameworks "
         "based on detailed specifications, ensuring adherence to coding standards and best practices.",
    backstory=(
        "A highly skilled software engineer specializing in code generation. This agent takes precise "
        "specifications for functions, classes, modules, or even entire applications and translates them "
        "into clean, efficient, and maintainable code. It is proficient in multiple programming languages "
        "and frameworks and is the cornerstone for all code generation tasks within the system. "
        "It prioritizes clarity, performance, and security in its generated code."
    ),
    tools=my_tools, # Tools might include linters, formatters, or code snippet libraries
    allow_delegation=False, # Typically, a writer agent executes directly
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
