"""Simple redaction of high-confidence secret-like values.

This is intentionally NOT a complete secret scanner. It removes a small set of
high-confidence patterns as a safety net; removing secrets before input is the
caller's responsibility.
"""

import re

REDACTED = "[REDACTED]"

_PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)

_BEARER_VALUE = re.compile(r"(?i)\bbearer\s+[a-z0-9\-._~+/=]{8,}")

# token=..., secret: "...", password = '...', api_key=... and api-key variants.
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(token|secret|password|api[_-]?key)(\s*[:=]\s*)"
    r"(\"[^\"]{4,}\"|'[^']{4,}'|[^\s\"',;]{4,})"
)


def redact_text(text: str) -> tuple[str, int]:
    """Redact secret-like values in ``text``. Return (redacted_text, count)."""
    count = 0

    text, n = _PRIVATE_KEY_BLOCK.subn(REDACTED, text)
    count += n

    text, n = _BEARER_VALUE.subn(REDACTED, text)
    count += n

    text, n = _SECRET_ASSIGNMENT.subn(lambda m: f"{m.group(1)}{m.group(2)}{REDACTED}", text)
    count += n

    return text, count


def redact_value(value):
    """Recursively redact all strings in a JSON-like value. Return (value, count)."""
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        redacted_items = []
        total = 0
        for item in value:
            redacted, count = redact_value(item)
            redacted_items.append(redacted)
            total += count
        return redacted_items, total
    if isinstance(value, dict):
        redacted_map = {}
        total = 0
        for key, item in value.items():
            redacted, count = redact_value(item)
            redacted_map[key] = redacted
            total += count
        return redacted_map, total
    return value, 0
