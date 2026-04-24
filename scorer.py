"""
scorer.py
Aggregates RuleResults into a weighted composite score and verdict.
All weights and thresholds come from config.yaml.
"""
 
from dataclasses import dataclass, field
from pathlib import Path
import yaml
 
from rules import RuleResult
 
 
@dataclass #dataclass automatically generates __init__
class AnalysisReport: #create a report for the input with an object
    input_type: str
    score: float
    verdict: str  # "clean" | "suspicious" | "phishing"
    triggered_rules: list[RuleResult] = field(default_factory=list) #each report gets their own list!
 
 
def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)
     #__file__ is the path of scorer.py itself. .parent is the directory containing it. This means config.yaml is always found
 
 
def score(rule_results: list[RuleResult], input_type: str) -> AnalysisReport: #this is the main function
    cfg = load_config()
    weights: dict = cfg.get("weights", {})
    thresholds: dict = cfg.get("thresholds", {"suspicious": 0.40, "phishing": 0.70})
 
    triggered = [r for r in rule_results if r.triggered] #filters down to rules that are flagged
 
    if not triggered:
        return AnalysisReport(
            input_type=input_type,
            score=0.0,
            verdict="clean",
            triggered_rules=[],
        )
 
    # Weighted average over triggered rules only
    total_weight = 0.0
    weighted_sum = 0.0
 
    for result in triggered:
        w = weights.get(result.rule_id, 0.5) #default to 0.5 rather than crashing
        weighted_sum += w * result.confidence
        total_weight += w
 
    composite = weighted_sum / total_weight if total_weight > 0 else 0.0 #find weighed avg
    composite = round(min(composite, 1.0), 4) 
 
    if composite >= thresholds["phishing"]: #0.70
        verdict = "phishing"
    elif composite >= thresholds["suspicious"]: #0.40
        verdict = "suspicious"
    else:
        verdict = "clean"
     #both of these cutoff videos come from config.yaml so i can edit sensitivity without touching code
 
    return AnalysisReport(
        input_type=input_type,
        score=composite,
        verdict=verdict,
        triggered_rules=triggered,
    )
 

