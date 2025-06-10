from crewai import Agent

queue_agent = Agent(
    role="Backend Queue Manager",
    goal="Manage and process asynchronous tasks and message queues for backend services",
    backstory="An agent focused on ensuring reliable and efficient task processing by managing message queues and handling asynchronous operations in the backend.",
    allow_delegation=False,
    verbose=True
)
