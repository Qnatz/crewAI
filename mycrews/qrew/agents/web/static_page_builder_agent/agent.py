from crewai import Agent

static_page_builder_agent = Agent(
    role="Static Web Page Builder",
    goal="Develop and maintain static web pages using HTML, CSS, and JavaScript",
    backstory="A web developer focused on creating fast, secure, and reliable static websites.",
    allow_delegation=False,
    verbose=True
)
