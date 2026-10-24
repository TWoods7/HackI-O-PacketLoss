"""Privacy filter (owner: JF). Everything sent to the browser or the LLM passes through scrub().

TODO(JF): extend patterns; add tests in backend/tests/test_privacy.py.
"""
import hashlib
import os
import re

_SALT = os.getenv("PREMISE_SALT", "change-me")

_PATTERNS = [
    re.compile(r"\b\d{9}\b"),            # raw premise_nu
    re.compile(r"\b37800\w{9}\b"),        # AEP location numbers (poles, transformers, devices)
    re.compile(r"\b\d{2,6}\s+[A-Z][A-Za-z]+(\s[A-Za-z]+)*\s(Rd|Road|St|Street|Ave|Avenue|Dr|Drive|Ln|Lane|Ct|Blvd|Way|Pike|Hwy)\b", re.I),
    re.compile(r"life\s*support", re.I),
]


def anon_premise(premise_nu: str) -> str:
    return "P-" + hashlib.sha256(f"{_SALT}:{premise_nu}".encode()).hexdigest()[:6].upper()


def scrub(text: str) -> str:
    for p in _PATTERNS:
        text = p.sub("[redacted]", text)
    return text
