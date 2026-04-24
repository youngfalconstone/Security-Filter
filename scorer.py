"""
scorer.py
Aggregates RuleResults into a weighted composite score and verdict.
All weights and thresholds come from config.yaml.
"""
 
from dataclasses import dataclass, field
from pathlib import Path
import yaml
 
from rules import RuleResult
 
 
@dataclass
class AnalysisReport:
    input_type: str
    score: float
    verdict: str  # "clean" | "suspicious" | "phishing"
    triggered_rules: list[RuleResult] = field(default_factory=list)
 
 
def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)
 
 
def score(rule_results: list[RuleResult], input_type: str) -> AnalysisReport:
    cfg = load_config()
    weights: dict = cfg.get("weights", {})
    thresholds: dict = cfg.get("thresholds", {"suspicious": 0.40, "phishing": 0.70})
 
    triggered = [r for r in rule_results if r.triggered]
 
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
        w = weights.get(result.rule_id, 0.5)
        weighted_sum += w * result.confidence
        total_weight += w
 
    composite = weighted_sum / total_weight if total_weight > 0 else 0.0
    composite = round(min(composite, 1.0), 4)
 
    if composite >= thresholds["phishing"]:
        verdict = "phishing"
    elif composite >= thresholds["suspicious"]:
        verdict = "suspicious"
    else:
        verdict = "clean"
 
    return AnalysisReport(
        input_type=input_type,
        score=composite,
        verdict=verdict,
        triggered_rules=triggered,
    )
 

