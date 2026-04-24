"""
main.py
CLI entrypoint. No detection logic lives here.
 
Usage:
    python main.py --type email --file sample.eml
    python main.py --type sms --file sample.txt
    cat sample.eml | python main.py --type email
"""
 
import argparse
import json
import sys
 
from parser import parse
from extractors import extract
from rules import evaluate
from scorer import score
 
 
def main():
    parser = argparse.ArgumentParser(
        description="Static phishing analysis engine for email and SMS."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["email", "sms"],
        help="Input content type.",
    )
    parser.add_argument(
        "--file",
        required=False,
        default=None,
        help="Path to input file. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON.",
    )
    args = parser.parse_args()
 
    # Read input
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()
 
    if not raw.strip():
        print("Error: empty input.", file=sys.stderr)
        sys.exit(1)
 
    # Pipeline
    parsed = parse(raw, args.type)
    features = extract(parsed)
    rule_results = evaluate(features)
    report = score(rule_results, args.type)
 
    # Output
    if args.json_output:
        out = {
            "input_type": report.input_type,
            "verdict": report.verdict,
            "score": report.score,
            "triggered_rules": [
                {
                    "rule_id": r.rule_id,
                    "confidence": r.confidence,
                    "evidence": r.evidence,
                }
                for r in report.triggered_rules
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"\n{'='*40}")
        print(f"  VERDICT : {report.verdict.upper()}")
        print(f"  SCORE   : {report.score:.4f}")
        print(f"  TYPE    : {report.input_type}")
        print(f"{'='*40}")
 
        if report.triggered_rules:
            print("\nTriggered Rules:")
            for r in report.triggered_rules:
                print(f"  [{r.rule_id}] confidence={r.confidence:.2f}")
                print(f"    {r.evidence}")
        else:
            print("\nNo indicators detected.")
        print()
 
 
if __name__ == "__main__":
    main()

