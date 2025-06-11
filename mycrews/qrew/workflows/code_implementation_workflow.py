import json
from ..agents.dev_utilities.code_writer_agent.agent import code_writer_agent
from ..agents.dev_utilities.tester_agent.agent import tester_agent
from ..crews.backend_development_crew import backend_development_crew
from ..crews.mobile_development_crew import mobile_development_crew
from ..crews.web_development_crew import web_development_crew
from crewai import Task # Assuming crewai is installed in the environment and accessible

def run_code_implementation_workflow(architecture_design):
    print("\n📦 Starting Code Implementation Workflow...")

    # 🔹 Breakdown architecture into module specs
    backend_spec = None
    mobile_spec = None
    web_spec = None

    # Attempt to extract specs from various possible structures of architecture_design
    if isinstance(architecture_design, dict):
        backend_spec = architecture_design.get("backend_spec")
        mobile_spec = architecture_design.get("mobile_spec")
        web_spec = architecture_design.get("web_spec")
    elif hasattr(architecture_design, 'raw_output') and architecture_design.raw_output:
        if isinstance(architecture_design.raw_output, dict):
            backend_spec = architecture_design.raw_output.get("backend_spec")
            mobile_spec = architecture_design.raw_output.get("mobile_spec")
            web_spec = architecture_design.raw_output.get("web_spec")
        elif isinstance(architecture_design.raw_output, str):
            try:
                parsed_output = json.loads(architecture_design.raw_output)
                if isinstance(parsed_output, dict):
                    backend_spec = parsed_output.get("backend_spec")
                    mobile_spec = parsed_output.get("mobile_spec")
                    web_spec = parsed_output.get("web_spec")
                else:
                    print(f"Warning: Parsed architecture_design.raw_output (from string) is not a dictionary. Type: {type(parsed_output)}. Specs will be None.")
            except json.JSONDecodeError:
                print(f"Warning: architecture_design.raw_output is a string but not valid JSON. Content: {architecture_design.raw_output[:200]}. Specs will be None.")
            except Exception as e:
                print(f"Error processing string architecture_design.raw_output: {e}. Specs will be None.")
        else:
            print(f"Warning: architecture_design.raw_output is of unhandled type: {type(architecture_design.raw_output)}. Specs will be None.")
    elif hasattr(architecture_design, 'raw') and isinstance(architecture_design.raw, dict):
        backend_spec = architecture_design.raw.get("backend_spec")
        mobile_spec = architecture_design.raw.get("mobile_spec")
        web_spec = architecture_design.raw.get("web_spec")
    elif hasattr(architecture_design, 'pydantic_output') and isinstance(architecture_design.pydantic_output, dict):
        backend_spec = architecture_design.pydantic_output.get("backend_spec")
        mobile_spec = architecture_design.pydantic_output.get("mobile_spec")
        web_spec = architecture_design.pydantic_output.get("web_spec")
    elif hasattr(architecture_design, 'get') and callable(getattr(architecture_design, 'get')):
        backend_spec = architecture_design.get("backend_spec")
        mobile_spec = architecture_design.get("mobile_spec")
        web_spec = architecture_design.get("web_spec")
    else:
        print(f"Warning: architecture_design (type: {type(architecture_design)}) is not a dictionary and does not have a directly usable .get() method or common CrewAI output attributes. Specs will likely be None.")

    results = []

    if backend_spec:
        print(f"Backend spec found. Preparing task for backend_development_crew. Spec: {str(backend_spec)[:100]}...")
        task_backend = Task(
            description="Implement backend APIs from architecture.",
            agent=code_writer_agent,
            expected_output="Python/FastAPI or NodeJS code implementing endpoints",
            context={ "spec": backend_spec },
            successCriteria=["compilable", "auth logic implemented", "modular code"]
        )
        if backend_development_crew:
            backend_development_crew.tasks = [task_backend]
            backend_result_item = backend_development_crew.kickoff()
            if backend_result_item is not None:
                 results.append(backend_result_item)
            else:
                print("Warning: backend_development_crew.kickoff() returned None.")
        else:
            print("Warning: backend_development_crew not available or not imported correctly.")
    else:
        print("Backend spec not found or is empty. Skipping backend development.")

    if mobile_spec:
        print(f"Mobile spec found. Preparing task for mobile_development_crew. Spec: {str(mobile_spec)[:100]}...")
        task_mobile = Task(
            description="Implement Android mobile UI from design spec.",
            agent=code_writer_agent,
            expected_output="Kotlin/Jetpack Compose code for mobile app UI",
            context={ "spec": mobile_spec },
            successCriteria=["UI matches design", "navigable", "reactive layout"]
        )
        if mobile_development_crew:
            mobile_development_crew.tasks = [task_mobile]
            mobile_result_item = mobile_development_crew.kickoff()
            if mobile_result_item is not None:
                results.append(mobile_result_item)
            else:
                print("Warning: mobile_development_crew.kickoff() returned None.")
        else:
            print("Warning: mobile_development_crew not available or not imported correctly.")
    else:
        print("Mobile spec not found or is empty. Skipping mobile development.")

    if web_spec:
        print(f"Web spec found. Preparing task for web_development_crew. Spec: {str(web_spec)[:100]}...")
        task_web = Task(
            description="Implement responsive web UI from design spec.",
            agent=code_writer_agent,
            expected_output="HTML/CSS/JS code for responsive site",
            context={ "spec": web_spec },
            successCriteria=["responsive layout", "semantic HTML"]
        )
        if web_development_crew:
            web_development_crew.tasks = [task_web]
            web_result_item = web_development_crew.kickoff()
            if web_result_item is not None:
                results.append(web_result_item)
            else:
                print("Warning: web_development_crew.kickoff() returned None.")
        else:
            print("Warning: web_development_crew not available or not imported correctly.")
    else:
        print("Web spec not found or is empty. Skipping web development.")

    if not results:
        print("No specs were processed, or all kickoff calls returned None/empty. Results list is empty.")
    else:
        print(f"Collected {len(results)} result(s) from dispatched crews.")

    print("✅ Code generation workflow finished.")
    return results
