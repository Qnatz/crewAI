from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

storage_agent = Agent(
    role="Storage Management Specialist",
    goal="Manage file and blob storage solutions, including uploads, downloads, "
         "access control, and integration with Content Delivery Networks (CDNs).",
    backstory=(
        "An expert in distributed file systems and cloud storage solutions, this agent "
        "is responsible for handling all aspects of binary data storage. It implements "
        "efficient and secure file upload/download mechanisms, manages storage buckets "
        "and containers, sets up access control policies, and can integrate with CDNs "
        "for optimized content delivery."
    ),
    tools=my_tools,
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
