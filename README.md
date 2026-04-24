# Security-Filter
Static analysis engine for detecting phishing indicators in email and SMS content using heuristic and pattern-based filtering.
Made as a practice project.

# Structure
parser.py — ingests raw email or SMS, returns a normalized dict with body, headers, urls, sender  

extractors.py — runs feature extraction on that dict: homograph detection, urgency phrases, structural flags. Returns a flat features: dict  

rules.py — stateless functions, each takes features, returns (rule_id, triggered: bool, confidence: float). No weights here.  

scorer.py — takes rule results, applies weights from config.yaml, returns final score + verdict string  

main.py — CLI only. Read input → call parser → extractors → rules → scorer → print report  

config.yaml — all tunables: weights, thresholds, regex patterns, shortener domain list

# Run
pip install pyyaml  

python main.py --type email --file sample.eml  

python main.py --type sms --file sample.txt --json  

cat sample.eml | python main.py --type email
