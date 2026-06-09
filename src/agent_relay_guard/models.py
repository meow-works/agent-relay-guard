"""Shared constants and deterministic derivations for agent-relay-guard."""

SCHEMA_VERSION = "1.0"

CARD_TYPES = ("progress", "instruction", "result")
RISK_LEVELS = ("low", "medium", "high", "critical", "unknown")
DECISIONS = ("APPROVE", "HOLD", "REJECT", "REVISE")

# Fixed decision options shown on every card, in fixed order.
DECISION_OPTIONS = list(DECISIONS)

DETAIL_PACKET_SUFFIX = "-detail"


def detail_packet_id(card_id: str) -> str:
    """Derive the detail packet id deterministically: ``{id}-detail``."""
    return f"{card_id}{DETAIL_PACKET_SUFFIX}"
