from crewai import Agent
from .tools import my_tools
from q_ware.llm_config import get_llm # Added import

llm_instance = get_llm() # Added instance

ios_ui_agent = Agent(
    role="iOS UI/UX Specialist",
    goal="Develop responsive and intuitive iOS user interfaces using SwiftUI or UIKit, "
         "based on design specifications and Apple's Human Interface Guidelines.",
    backstory=(
        "An expert in iOS UI development, this agent translates wireframes and mockups into "
        "pixel-perfect, functional user interfaces for Apple platforms. It is proficient in "
        "both modern declarative UI with SwiftUI and traditional UIKit. It focuses on creating "
        "engaging, accessible, and performant UIs that adhere to Apple's design principles "
        "and provide an excellent user experience on iPhone, iPad, and other iOS devices."
    ),
    tools=my_tools, # Tools might include UI component generators (SwiftUI views, UIKit elements), etc.
    allow_delegation=False,
    verbose=True,
    llm=llm_instance # Updated llm parameter
)
