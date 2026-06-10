import pytest

from agent_relay_guard.validation import (
    ValidationError,
    load_schema,
    unsupported_keywords,
    validate_input,
)


def test_sample_input_is_valid(sample_input):
    validate_input(sample_input)


@pytest.mark.parametrize(
    "field",
    [
        "schema_version",
        "id",
        "card_type",
        "title",
        "summary",
        "risk",
        "recommended_decision",
        "decision_reason",
        "next_action",
        "detail",
    ],
)
def test_missing_required_field_is_rejected(make_input, field):
    data = make_input()
    del data[field]
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    assert field in str(excinfo.value)


@pytest.mark.parametrize(
    "field",
    ["overview", "evidence", "changes", "open_questions"],
)
def test_missing_detail_field_is_rejected(make_input, field):
    data = make_input()
    del data["detail"][field]
    with pytest.raises(ValidationError):
        validate_input(data)


def test_schema_version_mismatch_is_rejected(make_input):
    data = make_input()
    data["schema_version"] = "2.0"
    with pytest.raises(ValidationError):
        validate_input(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("card_type", "report"),
        ("risk", "severe"),
        ("recommended_decision", "MERGE"),
    ],
)
def test_unknown_enum_value_is_rejected(make_input, field, value):
    data = make_input()
    data[field] = value
    with pytest.raises(ValidationError):
        validate_input(data)


@pytest.mark.parametrize("card_type", ["progress", "instruction", "result"])
def test_all_card_types_are_accepted(make_input, card_type):
    data = make_input()
    data["card_type"] = card_type
    validate_input(data)


@pytest.mark.parametrize("risk", ["low", "medium", "high", "critical", "unknown"])
def test_all_risk_levels_are_accepted(make_input, risk):
    data = make_input()
    data["risk"] = risk
    validate_input(data)


@pytest.mark.parametrize("decision", ["APPROVE", "HOLD", "REJECT", "REVISE"])
def test_all_decisions_are_accepted(make_input, decision):
    data = make_input()
    data["recommended_decision"] = decision
    validate_input(data)


def test_unknown_top_level_field_is_rejected(make_input):
    data = make_input()
    data["raw_logs"] = "not allowed"
    with pytest.raises(ValidationError):
        validate_input(data)


def test_empty_id_is_rejected(make_input):
    data = make_input()
    data["id"] = ""
    with pytest.raises(ValidationError):
        validate_input(data)


def test_non_string_evidence_item_is_rejected(make_input):
    data = make_input()
    data["detail"]["evidence"] = [{"nested": "object"}]
    with pytest.raises(ValidationError):
        validate_input(data)


def test_non_object_input_is_rejected():
    with pytest.raises(ValidationError):
        validate_input(["not", "an", "object"])


def test_top_level_missing_field_message_has_full_path(make_input):
    data = make_input()
    del data["risk"]
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    assert "$.risk: required field is missing" in excinfo.value.errors


def test_nested_missing_field_message_has_full_path(make_input):
    data = make_input()
    del data["detail"]["evidence"]
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    assert "$.detail.evidence: required field is missing" in excinfo.value.errors


def test_enum_message_has_path_value_and_allowed_values(make_input):
    data = make_input()
    data["risk"] = "severe"
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    [message] = excinfo.value.errors
    assert message.startswith("$.risk: invalid value 'severe'")
    for allowed in ("'low'", "'medium'", "'high'", "'critical'", "'unknown'"):
        assert allowed in message


def test_type_message_has_indexed_path_and_json_type_name(make_input):
    data = make_input()
    data["detail"]["evidence"] = ["fine", {"nested": "object"}]
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    assert "$.detail.evidence[1]: expected string, got object" in excinfo.value.errors


def test_type_message_uses_json_terms_for_other_types(make_input):
    data = make_input()
    data["detail"]["changes"] = [True, None]
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    assert "$.detail.changes[0]: expected string, got boolean" in excinfo.value.errors
    assert "$.detail.changes[1]: expected string, got null" in excinfo.value.errors


def test_long_invalid_enum_value_is_truncated(make_input):
    data = make_input()
    long_value = "x" * 500
    data["risk"] = long_value
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    [message] = excinfo.value.errors
    assert long_value not in message
    assert "...(truncated)" in message
    assert len(message) < 250


def test_control_characters_in_invalid_value_are_escaped(make_input):
    data = make_input()
    data["risk"] = "low\nfake-second-line: looks-official"
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    [message] = excinfo.value.errors
    assert "\n" not in message
    assert "\\n" in message


def test_unknown_field_with_newline_does_not_break_line_structure(make_input):
    data = make_input()
    data["bad\nfield"] = "x"
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    [message] = excinfo.value.errors
    assert "\n" not in message
    assert "$.bad\\nfield: unknown field" == message


def test_long_unknown_field_name_is_truncated(make_input):
    data = make_input()
    data["y" * 500] = "x"
    with pytest.raises(ValidationError) as excinfo:
        validate_input(data)
    [message] = excinfo.value.errors
    assert "y" * 500 not in message
    assert "...(truncated)" in message
    assert len(message) < 250


def test_schema_loads_and_declares_version_const():
    schema = load_schema()
    assert schema["properties"]["schema_version"]["const"] == "1.0"


def test_bundled_schema_uses_only_supported_keywords():
    assert unsupported_keywords(load_schema()) == set()


def test_unsupported_keyword_is_detected():
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "pattern": "^[a-z]+$"},
            "tags": {"type": "array", "items": {"type": "string", "maxLength": 10}},
        },
    }
    assert unsupported_keywords(schema) == {"pattern", "maxLength"}
