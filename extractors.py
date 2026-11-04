import re
from urllib.parse import urlparse
import yaml
from pathlib import Path
 
#read config.yaml from same directory as script...  supply phrase list and patterns used by extractors 
def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)
     
#take dict from parser.py and runs each detector and returns flat boolean/value dict for rules.py
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
 
#extract domain from From and Reply-To via regex and return True if they are different
def _check_sender_mismatch(sender: str, reply_to: str) -> bool:
    if not sender or not reply_to:
        return False
    sender_domain = _extract_domain_from_address(sender)
    reply_domain = _extract_domain_from_address(reply_to)
    if not sender_domain or not reply_domain:
        return False
    return sender_domain != reply_domain
 
 #detect domain with regex
def _extract_domain_from_address(addr: str) -> str:
    match = re.search(r"@([\w.\-]+)", addr)
    return match.group(1).lower() if match else ""

#detect impersonating domains
def _check_homograph(urls: list[str], targets: list[str]) -> bool:
    #this makes a translation table
    substitutions = str.maketrans("0123456789", "oizeasbtgq")
 
    for url in urls:
        try:
            domain = urlparse(url).netloc.lower()
            normalized = domain.translate(substitutions)
            #strip common endings for better matching
            base = re.sub(r"\.(com|net|org|io|co|info|biz).*$", "", normalized)
            #check if known brand name (e.g. "paypal") appears inside that normalized domain.
            for target in targets:
                #exclude exact matches by reconstructing what real domain would look like and comparing it against the original
                if target in base and domain != target + "." + domain.split(".")[-1]:
                    return True
        except Exception:
            continue
    return False
 
#immediately flag if a shortener is present
def _check_shortener(urls: list[str], shorteners: list[str]) -> bool:
    for url in urls:
        try:
            domain = urlparse(url).netloc.lower()
            if any(s in domain for s in shorteners):
                return True
        except Exception:
            continue
    return False
 
 #return true if any phrase from list is shown. remember, the list can be edited in config.yaml
def _check_phrases(body: str, phrases: list[str]) -> bool:
    return any(phrase in body for phrase in phrases)
 
#detect common HTML hiding techniques used in phishing
def _check_hidden_elements(html: str) -> bool:
    html = html[:MAX_HTML_CHARS]
    patterns = [
        r"display\s*:\s*none",
        r"visibility\s*:\s*hidden",
        r"font-size\s*:\s*0",
        r"opacity\s*:\s*0",
        r"color\s*:\s*#?fff(fff)?",  # white text on white background
    ]
    return any(re.search(p, html) for p in patterns)
 
MAX_HTML_CHARS = 2_000_000  # analysis is capped here; a phishing message does not need more than this to be judged

#detect anchor tags where visible text contains url that's different from href destination
def _check_mismatched_links(html: str) -> bool:
    html = html[:MAX_HTML_CHARS]
    #use regex to determine pattern. every repetition is bounded so a crafted message cannot make the
    #engine backtrack for seconds (regular-expression denial of service)
    anchor_pattern = re.compile(
        r'<a\s[^>]{0,500}?href=["\']([^"\']{1,2048})["\'][^>]{0,500}>([^<]{0,4000}(?:<(?!/a>)[^<]{0,4000}){0,50})</a>',
        re.IGNORECASE,
    )
    #find http(s) urls in text
    url_in_text = re.compile(r'https?://[\w./\-]{1,2048}')
    #finditer scans the full html and yields one match object per anchor tag found.
    for match in anchor_pattern.finditer(html):
        href = match.group(1).strip()
        text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        text_urls = url_in_text.findall(text)
        for text_url in text_urls:
            if urlparse(text_url).netloc != urlparse(href).netloc:
                return True
    return False

