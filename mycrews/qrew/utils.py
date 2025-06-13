# mycrews/qrew/utils.py
from datetime import datetime

class ErrorSummary:
    def __init__(self):
        self.records = []  # list of dicts: {stage, success, message, timestamp}

    def add(self, stage: str, success: bool, message: str = ""):
        # Truncate message to avoid long lines
        short_msg = (message[:200] + "...") if len(message) > 200 else message
        self.records.append({
            "stage": stage,
            "success": success,
            "message": short_msg,
            "timestamp": datetime.utcnow().isoformat()
        })

    def print(self):
        print("\n\n=== Workflow Summary ===")
        print(f"{'Stage':<25} {'Status':<8} {'Details'}")
        print("-" * 60)
        for record in self.records:
            status = "✅" if record["success"] else "❌"
            print(f"{record['stage']:<25} {status:<8} {record['message']}")
        print("=" * 60)

    def to_dict(self):
        return self.records.copy()
