import pytest
from src.app.analysis.human_audit import HumanAuditBenchmark


def test_human_audit_benchmark():
    audit = HumanAuditBenchmark()
    raw_records = [{"id": f"rec_{i}", "text": f"Review text for record {i} discussing groceries and delivery speed"} for i in range(50)]
    report = audit.run_benchmark(raw_records)
    assert report["sample_size_evaluated"] == 50
    assert "observed_agreement_percentage" in report
    assert report["precision"] > 0
    assert report["recall"] > 0
