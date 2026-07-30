"""CLI tool to execute Human Audit Benchmark sampling 200 raw sample reviews.

Usage:
    python scripts/run_audit.py
"""
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app.config import settings
from src.app.analysis.human_audit import HumanAuditBenchmark


def main():
    print("==========================================================")
    print("  Blinkit Discovery Engine — 200-Review Human Audit Tool ")
    print("==========================================================")
    
    raw_records = []
    json_path = os.path.join(settings.RAW_DATA_DIR, "all_raw_reviews.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_records = json.load(f)
        except Exception:
            pass

    audit_tool = HumanAuditBenchmark()
    report = audit_tool.run_benchmark(raw_records)

    print("\nHuman Audit Benchmark Verification Results:")
    for key, val in report.items():
        print(f"  - {key:<30}: {val}")
    print("==========================================================")


if __name__ == "__main__":
    main()
