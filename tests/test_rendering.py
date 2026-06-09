from agent_relay_guard.rendering import (
    build_card,
    build_detail,
    render_card_markdown,
    render_detail_markdown,
)

CARD_FIELDS = [
    "id",
    "card_type",
    "risk",
    "title",
    "summary",
    "recommended_decision",
    "decision_reason",
    "next_action",
    "detail_packet_id",
    "redaction_count",
    "options",
]

DETAIL_FIELDS = [
    "id",
    "detail_packet_id",
    "card_type",
    "risk",
    "overview",
    "evidence",
    "changes",
    "open_questions",
    "redaction_count",
]


def test_card_json_has_exactly_the_contract_fields(sample_input):
    card = build_card(sample_input)
    assert list(card.keys()) == CARD_FIELDS


def test_detail_packet_has_exactly_the_contract_fields(sample_input):
    packet = build_detail(sample_input)
    assert list(packet.keys()) == DETAIL_FIELDS


def test_detail_packet_id_is_deterministic(sample_input):
    card = build_card(sample_input)
    packet = build_detail(sample_input)
    assert card["detail_packet_id"] == "task-042-detail"
    assert packet["detail_packet_id"] == "task-042-detail"


def test_card_options_are_fixed(sample_input):
    card = build_card(sample_input)
    assert card["options"] == ["APPROVE", "HOLD", "REJECT", "REVISE"]


def test_redaction_count_is_present_even_when_zero(sample_input):
    assert build_card(sample_input)["redaction_count"] == 0
    assert build_detail(sample_input)["redaction_count"] == 0


def test_card_does_not_include_detail_bodies(sample_input):
    card = build_card(sample_input)
    card_markdown = render_card_markdown(card)
    for detail_text in (
        sample_input["detail"]["overview"],
        *sample_input["detail"]["evidence"],
        *sample_input["detail"]["changes"],
    ):
        assert detail_text not in card_markdown
        assert detail_text not in str(card.values())


def test_card_markdown_has_fixed_section_order(sample_input):
    markdown = render_card_markdown(build_card(sample_input))
    sections = [
        "# Fix flaky timing test in parser module (task-042)",
        "- Card type: result",
        "- Risk: low",
        "## Summary",
        "## Recommended decision",
        "## Next action",
        "## Decision options",
        "1. APPROVE / 2. HOLD / 3. REJECT / 4. REVISE",
        "Detail packet: task-042-detail",
    ]
    positions = [markdown.index(section) for section in sections]
    assert positions == sorted(positions)


def test_detail_markdown_contains_detail_bodies(sample_input):
    markdown = render_detail_markdown(build_detail(sample_input))
    assert sample_input["detail"]["overview"] in markdown
    for item in sample_input["detail"]["evidence"]:
        assert f"- {item}" in markdown
    assert "## Open questions" in markdown
    assert "(none)" in markdown


def test_markdown_and_json_card_carry_same_decision(sample_input):
    card = build_card(sample_input)
    markdown = render_card_markdown(card)
    assert card["recommended_decision"] in markdown
    assert card["decision_reason"] in markdown
    assert card["next_action"] in markdown


def test_secret_in_summary_is_redacted_in_card(make_input):
    data = make_input()
    data["summary"] = "Rotated credentials; old value was token=abcd1234."
    card = build_card(data)
    assert "abcd1234" not in card["summary"]
    assert card["redaction_count"] == 1
    assert "abcd1234" not in render_card_markdown(card)


def test_secret_in_detail_is_redacted_in_packet(make_input):
    data = make_input()
    data["detail"]["evidence"].append("log line: api_key=sk-fake-12345")
    packet = build_detail(data)
    assert "sk-fake-12345" not in str(packet["evidence"])
    assert packet["redaction_count"] == 1
    assert "sk-fake-12345" not in render_detail_markdown(packet)
