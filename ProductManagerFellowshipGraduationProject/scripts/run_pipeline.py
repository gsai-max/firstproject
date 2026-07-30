"""
CLI entrypoint for running the full discovery engine pipeline.
Usage: python scripts/run_pipeline.py --stage all

Stages:
  - scrape:  Collect feedback from all sources (Play Store, App Store, Reddit, Twitter, Forums)
  - process: Clean, deduplicate, and enrich data (Sentiment, Categories, Topics, Signals)
  - analyze: Extract themes, synthesize insights, and validate research question coverage
  - all:     Run all stages sequentially
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app.services.orchestrator import PipelineOrchestrator
from scripts.run_quality_audit import run_quality_audit


def main():
    parser = argparse.ArgumentParser(description="Run Blinkit AI Discovery Engine Pipeline")
    parser.add_argument(
        "--stage",
        type=str,
        default="all",
        choices=["scrape", "process", "analyze", "all"],
        help="Pipeline stage to run (scrape, process, analyze, all)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print(f"BLINKIT AI DISCOVERY ENGINE — PIPELINE EXECUTION ({args.stage.upper()})")
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    start_time = time.time()
    orchestrator = PipelineOrchestrator()
    results = orchestrator.run(stage=args.stage)
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Total Execution Time: {elapsed:.2f} seconds")
    
    for stage_name, res in results.items():
        print(f"\n[{stage_name.upper()} STAGE RESULTS]")
        if isinstance(res, dict):
            for k, v in res.items():
                print(f"  • {k}: {v}")
        else:
            print(f"  • {res}")

    # Automatically trigger Data Quality Audit if analysis stage was included
    if args.stage in ["analyze", "all"]:
        print("\n" + "=" * 70)
        print("RUNNING AUTOMATED DATA QUALITY AUDIT...")
        print("=" * 70)
        run_quality_audit()

    print("\n" + "=" * 70)
    print("Pipeline completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
