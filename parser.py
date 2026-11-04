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
 #take email or sms as input, then route depending on input type
 
def _parse_email(raw: str) -> dict: #note: remember this syntax - expect a str, and return dict
    msg = email.message_from_string(raw, policy=policy.default) #convert raw (str) to traversable object (headers, content type, etc)
 
    body = ""
    html_body = ""
 
    if msg.is_multipart(): #check attribute multipart of the traversable object
        for part in msg.walk():
         #ct stands for content type :)
            ct = part.get_content_type()
            if ct == "text/plain":
             #accumulate into body
                body += _content(part)
            elif ct == "text/html":
             #accumulate into html_body
                html_body += _content(part)
    else:
        ct = msg.get_content_type()
        if ct == "text/html":
         #accumulate into html_body
            html_body = _content(msg)
        else:
         #accumulate into body
            body = _content(msg)

 #fallback: if email only has html, strip the html tags for body
    if not body and html_body:
        body = re.sub(r"<[^>]+>", " ", html_body)
     
 #access object attributes for essential email data
    sender = str(msg.get("From", ""))
    reply_to = str(msg.get("Reply-To", ""))
    subject = str(msg.get("Subject", ""))
 
 #access the urls with internal function
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
 
 
def _content(part) -> str:
    """Decoded text of one MIME part. The input is hostile by definition, so a part that cannot be decoded
    (unknown charset, corrupt transfer encoding, non-text payload) becomes an empty string instead of an exception."""
    try:
        content = part.get_content()
    except Exception:  # noqa: BLE001 - the email package raises many unrelated types here
        return ""
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    return content if isinstance(content, str) else ""


def _parse_sms(raw: str) -> dict:
    # for better processing ,normalize unicode lookalikes
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
 
 #use regex search to find urls
MAX_URLS = 500  # more than this in one message is noise; it also bounds the work every URL check does


def _extract_urls(text: str) -> list[str]:
    pattern = r'https?://[^\s\'"<>]{1,2048}'
    return re.findall(pattern, text, re.IGNORECASE)[:MAX_URLS]
 
 
def _normalize_unicode(text: str) -> str:
    """Map common homoglyph characters to ASCII (a quality-of-life step).
    A production system would use the full confusables.txt dataset."""
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

