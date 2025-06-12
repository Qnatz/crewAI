import json
import os
import time # Added for simulating work
from pathlib import Path

# Assuming utils.py and project_manager.py are in the same directory
from utils import ErrorSummary
from project_manager import get_or_create_project

# 1. Define Your Stages
STAGES = [
    "initial_analysis",
    "content_generation",
    "review_and_edit",
    "final_assembly"
]

CHECKPOINT_FILE = ".qrew_checkpoint.json"

def load_progress():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed": {}, "results": {}}

def save_progress(progress):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(progress, f, indent=2)

# Placeholder functions for actual stage work
def run_stage_initial_analysis(common_kwargs):
    print(f"Running initial analysis with project path: {common_kwargs.get('project_path')}")
    time.sleep(2) # Simulate work
    if common_kwargs.get("simulate_error_at_stage") == "initial_analysis":
        raise ValueError("Simulated error in initial_analysis")
    return {"analysis_summary": "Initial analysis complete.", "data_points": [1, 2, 3]}

def run_stage_content_generation(analysis_result, common_kwargs):
    print(f"Running content generation based on: {analysis_result.get('analysis_summary')}")
    print(f"Project path for content generation: {common_kwargs.get('project_path')}")
    time.sleep(3) # Simulate work
    if common_kwargs.get("simulate_error_at_stage") == "content_generation":
        raise RuntimeError("Simulated error in content_generation")
    return {"generated_content": "This is the generated content.", "version": "1.0"}

def run_stage_review_and_edit(content_result, common_kwargs):
    print(f"Running review and edit for content: {content_result.get('generated_content')}")
    print(f"Project path for review: {common_kwargs.get('project_path')}")
    time.sleep(2) # Simulate work
    if common_kwargs.get("simulate_error_at_stage") == "review_and_edit":
        # Simulate a long error message
        raise Exception("Simulated error in review_and_edit: " + "long_message_" * 30)
    return {"edited_content": "This is the reviewed and edited content.", "feedback_notes": "All good."}

def run_stage_final_assembly(edited_content_result, common_kwargs):
    print(f"Running final assembly with: {edited_content_result.get('edited_content')}")
    print(f"Project path for assembly: {common_kwargs.get('project_path')}")
    time.sleep(1) # Simulate work
    if common_kwargs.get("simulate_error_at_stage") == "final_assembly":
        raise ConnectionError("Simulated error in final_assembly")
    # Example of writing to project path
    output_file = Path(common_kwargs["project_path"]) / "final_output.txt"
    output_file.write_text(f"Final assembled content: {edited_content_result.get('edited_content')}\nNotes: {edited_content_result.get('feedback_notes')}")
    print(f"Final output written to {output_file}")
    return {"final_product_path": str(output_file), "status": "successfully assembled"}


def run_resumable_pipeline(user_request, project_goal, priority, simulate_error_at_stage=None):
    summary = ErrorSummary()
    progress = load_progress()

    # 2) Resolve project folder
    # Use project_goal as the name for project creation
    proj = get_or_create_project(project_goal)
    print(f"Project '{proj['name']}' status: {proj['status']}, folder at {proj['path']}")

    # 3) Include project info in every Task’s kwargs
    common_kwargs = {
        "user_request": user_request,
        "project_id": proj["id"],
        "project_path": proj["path"],
        "project_goal": project_goal,
        "priority": priority,
        "simulate_error_at_stage": simulate_error_at_stage # For testing error handling
    }

    # Stage 1: Initial Analysis
    stage_name_1 = STAGES[0]
    try:
        if not progress["completed"].get(stage_name_1):
            print(f"▶ Stage 1: {stage_name_1}")
            # tm_task = Task( … ) # build as before
            # tm_result = qrew_main_crew.delegate_task(task=tm_task)
            # progress["results"]["taskmaster_analysis"] = tm_result.raw
            result_stage_1 = run_stage_initial_analysis(common_kwargs)
            progress["results"][stage_name_1] = result_stage_1 # Store raw or minimal serializable output
            progress["completed"][stage_name_1] = True
            save_progress(progress)
            summary.add(stage_name_1, True)
            print(f"✅ Stage 1: {stage_name_1} completed.")
        else:
            result_stage_1 = progress["results"][stage_name_1]
            summary.add(stage_name_1, True, "Skipped (already done)")
            print(f"↪ Skipping Stage 1: {stage_name_1} (already done)")
    except Exception as e:
        print(f"❌ Error in Stage 1: {stage_name_1} - {e}")
        summary.add(stage_name_1, False, str(e))
        save_progress(progress) # Save progress even on error to not repeat this stage if it failed partway
        summary.print()
        return progress["results"] # Exit early or decide how to handle partial failure

    # Stage 2: Content Generation
    stage_name_2 = STAGES[1]
    try:
        if not progress["completed"].get(stage_name_2):
            print(f"▶ Stage 2: {stage_name_2}")
            # Pass result of stage 1 to stage 2
            result_stage_2 = run_stage_content_generation(result_stage_1, common_kwargs)
            progress["results"][stage_name_2] = result_stage_2
            progress["completed"][stage_name_2] = True
            save_progress(progress)
            summary.add(stage_name_2, True)
            print(f"✅ Stage 2: {stage_name_2} completed.")
        else:
            result_stage_2 = progress["results"][stage_name_2]
            summary.add(stage_name_2, True, "Skipped (already done)")
            print(f"↪ Skipping Stage 2: {stage_name_2} (already done)")
    except Exception as e:
        print(f"❌ Error in Stage 2: {stage_name_2} - {e}")
        summary.add(stage_name_2, False, str(e))
        save_progress(progress)
        summary.print()
        return progress["results"]

    # Stage 3: Review and Edit
    stage_name_3 = STAGES[2]
    try:
        if not progress["completed"].get(stage_name_3):
            print(f"▶ Stage 3: {stage_name_3}")
            result_stage_3 = run_stage_review_and_edit(result_stage_2, common_kwargs)
            progress["results"][stage_name_3] = result_stage_3
            progress["completed"][stage_name_3] = True
            save_progress(progress)
            summary.add(stage_name_3, True)
            print(f"✅ Stage 3: {stage_name_3} completed.")
        else:
            result_stage_3 = progress["results"][stage_name_3] # Load if skipped
            summary.add(stage_name_3, True, "Skipped (already done)")
            print(f"↪ Skipping Stage 3: {stage_name_3} (already done)")
    except Exception as e:
        print(f"❌ Error in Stage 3: {stage_name_3} - {e}")
        summary.add(stage_name_3, False, str(e))
        save_progress(progress)
        summary.print()
        return progress["results"]

    # Stage 4: Final Assembly
    stage_name_4 = STAGES[3]
    try:
        if not progress["completed"].get(stage_name_4):
            print(f"▶ Stage 4: {stage_name_4}")
            result_stage_4 = run_stage_final_assembly(result_stage_3, common_kwargs)
            progress["results"][stage_name_4] = result_stage_4
            progress["completed"][stage_name_4] = True
            save_progress(progress)
            summary.add(stage_name_4, True)
            print(f"✅ Stage 4: {stage_name_4} completed.")
        else:
            # result_stage_4 = progress["results"][stage_name_4] # Not strictly needed if it's the last stage and we only care about completion
            summary.add(stage_name_4, True, "Skipped (already done)")
            print(f"↪ Skipping Stage 4: {stage_name_4} (already done)")
    except Exception as e:
        print(f"❌ Error in Stage 4: {stage_name_4} - {e}")
        summary.add(stage_name_4, False, str(e))
        save_progress(progress)
        summary.print()
        return progress["results"]


    print("\n✅ Pipeline complete.")
    summary.print()
    return progress["results"]

if __name__ == "__main__":
    print("🚀 Starting Resumable Pipeline Execution...")
    # Sample inputs
    user_request_input = "Develop a new feature for our e-commerce platform."
    project_goal_input = "Feature: Enhanced Product Recommendation Engine"
    priority_input = "High"

    # To test error handling and resumability:
    # 1. Run once without simulate_error_at_stage. All stages should complete.
    #    A .qrew_checkpoint.json and projects/ directory will be created.
    # 2. Rerun. All stages should be skipped.
    # 3. Delete .qrew_checkpoint.json.
    # 4. Run with simulate_error_at_stage="content_generation".
    #    The pipeline will stop at stage 2. .qrew_checkpoint.json will show stage 1 completed.
    # 5. Rerun with simulate_error_at_stage=None (or remove the arg).
    #    Pipeline should skip stage 1 and resume from stage 2.
    #    If the error simulation was for stage 2, it will re-attempt stage 2.

    # Example: Simulate an error in 'content_generation' stage for the first run
    # results = run_resumable_pipeline(user_request_input, project_goal_input, priority_input, simulate_error_at_stage="content_generation")

    # Normal run
    results = run_resumable_pipeline(user_request_input, project_goal_input, priority_input)

    print("\n🏁 Pipeline execution finished. Final Results:")
    print(json.dumps(results, indent=2))

    # To clean up for a fresh run:
    # if os.path.exists(CHECKPOINT_FILE):
    #     os.remove(CHECKPOINT_FILE)
    #     print(f"\n🧹 Cleaned up {CHECKPOINT_FILE}")
    # print("Consider cleaning up the 'projects/' directory manually if needed.")
