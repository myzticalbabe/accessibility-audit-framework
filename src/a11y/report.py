"""JSON report generation."""
import json
from .checks import CheckResult, run_all


def generate_report(html: str) -> dict:
    results = run_all(html)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "checks": [
            {"rule": r.rule, "passed": r.passed, "message": r.message}
            for r in results
        ],
    }


def report_to_json(html: str, indent: int = 2) -> str:
    return json.dumps(generate_report(html), indent=indent)
