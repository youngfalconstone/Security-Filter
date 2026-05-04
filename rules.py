#return result... no weighing involved
 
from dataclasses import dataclass
from typing import Callable
 
 
@dataclass
class RuleResult:
    rule_id: str
    triggered: bool
    confidence: float  # 0.0–1.0, only meaningful when triggered=True
    evidence: str
 
 
#individual rules
 
def rule_homograph(features: dict) -> RuleResult:
    triggered = features.get("homograph_detected", False)
    return RuleResult(
        rule_id="homograph_detected",
        triggered=triggered,
        confidence=1.0 if triggered else 0.0,
        evidence="Domain contains lookalike characters mimicking a known brand." if triggered else "",
    )
 
 
def rule_sender_mismatch(features: dict) -> RuleResult:
    triggered = features.get("sender_mismatch", False)
    return RuleResult(
        rule_id="sender_mismatch",
        triggered=triggered,
        confidence=1.0 if triggered else 0.0,
        evidence="From address domain differs from Reply-To domain." if triggered else "",
    )
 
 
def rule_url_shortener(features: dict) -> RuleResult:
    triggered = features.get("url_shortener", False)
    return RuleResult(
        rule_id="url_shortener",
        triggered=triggered,
        confidence=0.7 if triggered else 0.0,
        evidence="Message contains a known URL shortener link." if triggered else "",
    )
 
 
def rule_urgency_language(features: dict) -> RuleResult:
    triggered = features.get("urgency_language", False)
    return RuleResult(
        rule_id="urgency_language",
        triggered=triggered,
        confidence=0.8 if triggered else 0.0,
        evidence="Body contains urgency or threat language." if triggered else "",
    )
 
 
def rule_credential_request(features: dict) -> RuleResult:
    triggered = features.get("credential_request", False)
    return RuleResult(
        rule_id="credential_request",
        triggered=triggered,
        confidence=1.0 if triggered else 0.0,
        evidence="Body explicitly solicits credentials or sensitive personal data." if triggered else "",
    )
 
 
def rule_hidden_elements(features: dict) -> RuleResult:
    triggered = features.get("hidden_elements", False)
    return RuleResult(
        rule_id="hidden_elements",
        triggered=triggered,
        confidence=0.9 if triggered else 0.0,
        evidence="HTML contains elements hidden via CSS (display:none, opacity:0, etc.)." if triggered else "",
    )
 
 
def rule_mismatched_link_text(features: dict) -> RuleResult:
    triggered = features.get("mismatched_link_text", False)
    return RuleResult(
        rule_id="mismatched_link_text",
        triggered=triggered,
        confidence=0.9 if triggered else 0.0,
        evidence="Anchor tag visible URL does not match href destination domain." if triggered else "",
    )
 
 
#all rules for iteration
RULES: list[Callable[[dict], RuleResult]] = [
    rule_homograph,
    rule_sender_mismatch,
    rule_url_shortener,
    rule_urgency_language,
    rule_credential_request,
    rule_hidden_elements,
    rule_mismatched_link_text,
]
 
#function to iterate through rules to return ruleresult objects
def evaluate(features: dict) -> list[RuleResult]:
    return [rule(features) for rule in RULES]

