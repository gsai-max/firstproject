"""CLI entrypoint for running Phase 4: 6-Agent AI Analysis Layer & Behavior Graph Engine.

Usage:
    python scripts/analyze_only.py
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app.services.orchestrator import PipelineOrchestrator


def main():
    print("==========================================================")
    print("  Blinkit Discovery Engine — Phase 4: 6-Agent AI Pipeline ")
    print("==========================================================")
    orchestrator = PipelineOrchestrator()
    results = orchestrator.run(stage="analyze")
    
    print("\nPhase 4 Analysis & Behavior Graph Construction Summary:")
    analyze_res = results.get("analyze", {})
    for key, val in analyze_res.items():
        print(f"  - {key:<32}: {val}")
    print("==========================================================")


if __name__ == "__main__":
    main()
