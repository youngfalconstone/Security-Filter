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

