# Security-Filter
Static analysis engine for detecting phishing indicators in email and SMS content using heuristic and pattern-based filtering.
Made as a practice project.

# Structure
parser.py : ingests raw email or SMS, returns a dict with body, headers, urls, sender  

extractors.py : runs feature extraction on that dict - homograph detection, urgency phrases, structural flags. returns a flat features: dict  

rules.py : stateless functions, each takes features, returns (rule_id, triggered: bool, confidence: float).

scorer.py : takes rule results, applies weights from config.yaml, returns final weighed score + verdict  

main.py : CLI only! Read input, call parser, extractors, rules, scorer, then report  

config.yaml : all editable: weights, thresholds, regex patterns, shortener domain list, etc

# Notes
The input is treated as hostile: it is size-capped, decoded leniently, MIME parts that fail to decode are skipped,
and every regular expression that runs over the message is bounded so a crafted message cannot stall the analysis.
Use generative AI to make more sample messages for testing; `samples.eml` is one phishing example.

# Run
pip install pyyaml  

python main.py --type email --file sample.eml  

python main.py --type sms --file sample.txt --json  

cat sample.eml | python main.py --type email
