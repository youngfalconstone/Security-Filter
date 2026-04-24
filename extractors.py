"""
extractors.py
Runs feature extraction on a parsed message dict.
Returns a flat features dict consumed by rules.py.
"""
 
import re
from urllib.parse import urlparse
import yaml
from pathlib import Path
 
 
def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)
 
 
def extract(parsed: dict) -> dict:
    cfg = load_config()
    patterns = cfg.get("patterns", {})
 
    urls = parsed.get("urls", [])
    body = parsed.get("body", "").lower()
    html_body = parsed.get("html_body", "").lower()
    sender = parsed.get("sender", "")
    reply_to = parsed.get("reply_to", "")
 
    return {
        "urls": urls,
        "sender_mismatch": _check_sender_mismatch(sender, reply_to),
        "homograph_detected": _check_homograph(urls, patterns.get("homograph_targets", [])),
        "url_shortener": _check_shortener(urls, patterns.get("known_shorteners", [])),
        "urgency_language": _check_phrases(body, patterns.get("urgency_phrases", [])),
        "credential_request": _check_phrases(body, patterns.get("credential_phrases", [])),
        "hidden_elements": _check_hidden_elements(html_body),
        "mismatched_link_text": _check_mismatched_links(html_body),
    }
 
 
def _check_sender_mismatch(sender: str, reply_to: str) -> bool:
    if not sender or not reply_to:
        return False
    sender_domain = _extract_domain_from_address(sender)
    reply_domain = _extract_domain_from_address(reply_to)
    if not sender_domain or not reply_domain:
        return False
    return sender_domain != reply_domain
 
 
def _extract_domain_from_address(addr: str) -> str:
    match = re.search(r"@([\w.\-]+)", addr)
    return match.group(1).lower() if match else ""
 
 
def _check_homograph(urls: list[str], targets: list[str]) -> bool:
    """
    Detect lookalike domains: e.g. paypa1.com, arnazon.com
    Checks for known brand names with substituted characters.
    """
    substitutions = str.maketrans("0123456789", "oizeasbtgq")
 
    for url in urls:
        try:
            domain = urlparse(url).netloc.lower()
            normalized = domain.translate(substitutions)
            # Strip common TLDs for matching
            base = re.sub(r"\.(com|net|org|io|co|info|biz).*$", "", normalized)
            for target in targets:
                if target in base and domain != target + "." + domain.split(".")[-1]:
                    return True
        except Exception:
            continue
    return False
 
 
def _check_shortener(urls: list[str], shorteners: list[str]) -> bool:
    for url in urls:
        try:
            domain = urlparse(url).netloc.lower()
            if any(s in domain for s in shorteners):
                return True
        except Exception:
            continue
    return False
 
 
def _check_phrases(body: str, phrases: list[str]) -> bool:
    return any(phrase in body for phrase in phrases)
 
 
def _check_hidden_elements(html: str) -> bool:
    """
    Detect common HTML hiding techniques used in phishing:
    - display:none / visibility:hidden
    - font-size:0
    - opacity:0
    """
    patterns = [
        r"display\s*:\s*none",
        r"visibility\s*:\s*hidden",
        r"font-size\s*:\s*0",
        r"opacity\s*:\s*0",
        r"color\s*:\s*#?fff(fff)?",  # white text on white background
    ]
    return any(re.search(p, html) for p in patterns)
 
 
def _check_mismatched_links(html: str) -> bool:
    """
    Detect anchor tags where visible text contains a URL
    that differs from the href destination.
    """
    anchor_pattern = re.compile(
        r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    url_in_text = re.compile(r'https?://[\w./\-]+')
 
    for match in anchor_pattern.finditer(html):
        href = match.group(1).strip()
        text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        text_urls = url_in_text.findall(text)
        for text_url in text_urls:
            if urlparse(text_url).netloc != urlparse(href).netloc:
                return True
    return False

