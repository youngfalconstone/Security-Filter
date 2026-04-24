"""
parser.py
Ingests raw email (MIME) or SMS (plaintext) and returns a normalized dict.
"""
 
import email
import re
from email import policy
from typing import Literal
 
 
def parse(raw: str, input_type: Literal["email", "sms"]) -> dict:
    if input_type == "email":
        return _parse_email(raw)
    elif input_type == "sms":
        return _parse_sms(raw)
    else:
        raise ValueError(f"Unsupported input_type: {input_type}")
 
 
def _parse_email(raw: str) -> dict:
    msg = email.message_from_string(raw, policy=policy.default)
 
    body = ""
    html_body = ""
 
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                body += part.get_content() or ""
            elif ct == "text/html":
                html_body += part.get_content() or ""
    else:
        ct = msg.get_content_type()
        if ct == "text/html":
            html_body = msg.get_content() or ""
        else:
            body = msg.get_content() or ""
 
    # Fallback: strip HTML tags for plain body if only HTML present
    if not body and html_body:
        body = re.sub(r"<[^>]+>", " ", html_body)
 
    sender = str(msg.get("From", ""))
    reply_to = str(msg.get("Reply-To", ""))
    subject = str(msg.get("Subject", ""))
 
    urls = _extract_urls(body + " " + html_body)
 
    return {
        "input_type": "email",
        "sender": sender,
        "reply_to": reply_to,
        "subject": subject,
        "body": body,
        "html_body": html_body,
        "urls": urls,
        "headers": dict(msg.items()),
    }
 
 
def _parse_sms(raw: str) -> dict:
    # Normalize unicode lookalikes before processing
    normalized = _normalize_unicode(raw)
    urls = _extract_urls(normalized)
 
    return {
        "input_type": "sms",
        "sender": "",
        "reply_to": "",
        "subject": "",
        "body": normalized,
        "html_body": "",
        "urls": urls,
        "headers": {},
    }
 
 
def _extract_urls(text: str) -> list[str]:
    pattern = r'https?://[^\s\'"<>]+'
    return re.findall(pattern, text, re.IGNORECASE)
 
 
def _normalize_unicode(text: str) -> str:
    """
    Naive unicode normalization: map common homoglyph characters to ASCII.
    A production system would use the full confusables.txt dataset.
    """
    replacements = {
        "\u0430": "a",  # Cyrillic а
        "\u0435": "e",  # Cyrillic е
        "\u043e": "o",  # Cyrillic о
        "\u0440": "p",  # Cyrillic р
        "\u0441": "c",  # Cyrillic с
        "\u0445": "x",  # Cyrillic х
        "\u0456": "i",  # Cyrillic і
        "\u04cf": "l",  # Cyrillic ӏ
        "\u2080": "0",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text

