from typing import Dict, Optional

class LLMConfig:
    GENERAL_THRESHOLD_COMPLEXITY = 7

    AGENT_CONFIGS: Dict[str, Dict[str, any]] = {
        # Marketing Agent Configuration
        "src/crew/agents/marketing/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 6,
            "always_2.0": False,
        },
        # Research Agent Configuration
        "src/crew/agents/research/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7,
            "always_2.0": False,
        },
        # Writer Agent Configuration
        "src/crew/agents/writer/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 8,
            "always_2.0": False,
        },
        # Coder Agent Configuration
        "src/crew/agents/coder/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 9,
            "always_2.0": True, # Always use gemini-2.0-flash for coder agent
        },
         # Generalist Agent Configuration
        "src/crew/agents/generalist/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7, # Standard threshold
            "always_2.0": False,
        },
        # Data Analyst Agent Configuration
        "src/crew/agents/data_analyst/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 8,
            "always_2.0": False,
        },
        # HR Agent Configuration
        "src/crew/agents/hr/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 6,
            "always_2.0": False,
        },
        # Finance Agent Configuration
        "src/crew/agents/finance/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 8,
            "always_2.0": False,
        },
        # Legal Agent Configuration
        "src/crew/agents/legal/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 9,
            "always_2.0": True, # Always use gemini-2.0-flash for legal agent
        },
        # Healthcare Agent Configuration
        "src/crew/agents/healthcare/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 8,
            "always_2.0": False,
        },
        # Education Agent Configuration
        "src/crew/agents/education/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7,
            "always_2.0": False,
        },
         # Customer Support Agent Configuration
        "src/crew/agents/customer_support/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 6,
            "always_2.0": False,
        },
        # Real Estate Agent Configuration
        "src/crew/agents/real_estate/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7,
            "always_2.0": False,
        },
        # Travel Agent Configuration
        "src/crew/agents/travel/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 6,
            "always_2.0": False,
        },
        # Content Creator Agent Configuration
        "src/crew/agents/content_creator/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7,
            "always_2.0": False,
        },
        # Sales Agent Configuration
        "src/crew/agents/sales/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7,
            "always_2.0": False,
        },
        # Project Manager Agent Configuration
        "src/crew/agents/project_manager/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 8,
            "always_2.0": False,
        },
        # Event Planner Agent Configuration
        "src/crew/agents/event_planner/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 6,
            "always_2.0": False,
        },
        # Fitness Coach Agent Configuration
        "src/crew/agents/fitness_coach/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7,
            "always_2.0": False,
        },
        # Chef Agent Configuration
        "src/crew/agents/chef/agent.py": {
            "default_model": "gemini-1.5-flash",
            "threshold": 7,
            "always_2.0": False,
        },
    }

    @classmethod
    def select_model(
        cls,
        agent_module_path: Optional[str],
        complexity_score: Optional[int],
        current_model_name: str,
    ) -> str:
        if agent_module_path and agent_module_path in cls.AGENT_CONFIGS:
            config = cls.AGENT_CONFIGS[agent_module_path]
            if config["always_2.0"]:
                return "gemini-2.0-flash"
            if complexity_score is not None:
                if complexity_score >= config["threshold"]:
                    return "gemini-2.0-flash"
                else:
                    return "gemini-1.5-flash"
            return config["default_model"]

        if complexity_score is not None:
            if complexity_score >= cls.GENERAL_THRESHOLD_COMPLEXITY:
                return "gemini-2.0-flash"
            else:
                return "gemini-1.5-flash"

        return current_model_name
