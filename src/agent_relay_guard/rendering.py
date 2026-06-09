"""Build and render routine cards and detail packets.

Routine cards are built only from whitelisted short fields and never include
detail bodies. Detail packets carry the long-form content. Both outputs are
redacted and always carry ``redaction_count`` (even when it is 0).
"""

from .models import DECISION_OPTIONS, detail_packet_id
from .redaction import redact_value

_CARD_SOURCE_FIELDS = (
    "id",
    "card_type",
    "risk",
    "title",
    "summary",
    "recommended_decision",
    "decision_reason",
    "next_action",
)

_DETAIL_SOURCE_FIELDS = ("overview", "evidence", "changes", "open_questions")


def build_card(data: dict) -> dict:
    """Build the routine card JSON object from validated input."""
    fields = {key: data[key] for key in _CARD_SOURCE_FIELDS}
    fields, count = redact_value(fields)
    return {
        "id": fields["id"],
        "card_type": fields["card_type"],
        "risk": fields["risk"],
        "title": fields["title"],
        "summary": fields["summary"],
        "recommended_decision": fields["recommended_decision"],
        "decision_reason": fields["decision_reason"],
        "next_action": fields["next_action"],
        "detail_packet_id": detail_packet_id(fields["id"]),
        "redaction_count": count,
        "options": list(DECISION_OPTIONS),
    }


def build_detail(data: dict) -> dict:
    """Build the detail packet JSON object from validated input."""
    fields = {
        "id": data["id"],
        "card_type": data["card_type"],
        "risk": data["risk"],
        **{key: data["detail"][key] for key in _DETAIL_SOURCE_FIELDS},
    }
    fields, count = redact_value(fields)
    return {
        "id": fields["id"],
        "detail_packet_id": detail_packet_id(fields["id"]),
        "card_type": fields["card_type"],
        "risk": fields["risk"],
        "overview": fields["overview"],
        "evidence": fields["evidence"],
        "changes": fields["changes"],
        "open_questions": fields["open_questions"],
        "redaction_count": count,
    }


def _options_line() -> str:
    return " / ".join(
        f"{number}. {option}" for number, option in enumerate(DECISION_OPTIONS, start=1)
    )


def render_card_markdown(card: dict) -> str:
    """Render a routine card as Markdown with a fixed section order."""
    lines = [
        f"# {card['title']} ({card['id']})",
        "",
        f"- Card type: {card['card_type']}",
        f"- Risk: {card['risk']}",
        "",
        "## Summary",
        "",
        card["summary"],
        "",
        "## Recommended decision",
        "",
        card["recommended_decision"],
        "",
        f"Reason: {card['decision_reason']}",
        "",
        "## Next action",
        "",
        card["next_action"],
        "",
        "## Decision options",
        "",
        _options_line(),
        "",
        f"Detail packet: {card['detail_packet_id']}",
    ]
    return "\n".join(lines) + "\n"


def _bullet_list(items: list[str]) -> list[str]:
    if not items:
        return ["(none)"]
    return [f"- {item}" for item in items]


def render_detail_markdown(packet: dict) -> str:
    """Render a detail packet as Markdown with a fixed section order."""
    lines = [
        f"# Detail packet: {packet['detail_packet_id']}",
        "",
        f"- Card ID: {packet['id']}",
        f"- Card type: {packet['card_type']}",
        f"- Risk: {packet['risk']}",
        f"- Redactions: {packet['redaction_count']}",
        "",
        "## Overview",
        "",
        packet["overview"],
        "",
        "## Evidence",
        "",
        *_bullet_list(packet["evidence"]),
        "",
        "## Changes",
        "",
        *_bullet_list(packet["changes"]),
        "",
        "## Open questions",
        "",
        *_bullet_list(packet["open_questions"]),
    ]
    return "\n".join(lines) + "\n"
