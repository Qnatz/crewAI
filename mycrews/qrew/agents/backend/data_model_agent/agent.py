from crewai import Agent

data_model_agent = Agent(
    role="Backend Data Modeler",
    goal="Design and maintain data models for backend databases and applications",
    backstory="A data-centric agent specializing in creating efficient and scalable data models to support backend application requirements.",
    allow_delegation=False,
    verbose=True
)
