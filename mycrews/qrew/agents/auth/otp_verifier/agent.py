from crewai import Agent

otp_verifier_agent = Agent(
    role="OTP Verifier",
    goal="Verify one-time passwords (OTPs) for user authentication",
    backstory="A specialized agent focused on verifying OTPs to enhance the security of user accounts during login and other sensitive operations.",
    allow_delegation=False,
    verbose=True
)
