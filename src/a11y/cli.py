"""CLI for accessibility audit."""
import argparse

from .report import report_to_json


def main(argv=None):
    parser = argparse.ArgumentParser(description="Accessibility Audit")
    parser.add_argument("file", help="HTML file to audit")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    with open(args.file) as f:
        html = f.read()

    if args.json:
        print(report_to_json(html))
    else:
        import json
        report = json.loads(report_to_json(html))
        print(f"Total: {report['total']}, Passed: {report['passed']}, Failed: {report['failed']}")
        for c in report["checks"]:
            status = "PASS" if c["passed"] else "FAIL"
            print(f"  [{status}] {c['rule']}: {c['message']}")


if __name__ == "__main__":
    main()
