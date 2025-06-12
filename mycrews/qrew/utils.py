# mycrews/qrew/utils.py
class ErrorSummary:
    def __init__(self):
        self.records = []  # list of (stage, success, message)

    def add(self, stage: str, success: bool, message: str = ""):
        # Truncate message to avoid insanely long lines
        short_msg = (message[:200] + "...") if len(message) > 200 else message
        self.records.append((stage, success, short_msg))

    def print(self):
        print("\n\n=== Workflow Summary ===")
        print(f"{'Stage':<30} {'Status':<8} {'Error (if any)'}")
        print("-" * 70)
        for stage, success, msg in self.records:
            status = "✅" if success else "❌"
            print(f"{stage:<30} {status:<8} {msg}")
        print("=" * 70)
