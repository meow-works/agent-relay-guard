from agent_relay_guard.redaction import REDACTED, redact_text, redact_value


def test_bearer_value_is_redacted():
    text, count = redact_text("Header was Authorization: Bearer abcd1234efgh5678")
    assert "abcd1234efgh5678" not in text
    assert REDACTED in text
    assert count == 1


def test_private_key_block_is_redacted():
    block = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA\nfakekeymaterial\n"
        "-----END RSA PRIVATE KEY-----"
    )
    text, count = redact_text(f"found key: {block} in log")
    assert "fakekeymaterial" not in text
    assert REDACTED in text
    assert count == 1


def test_secret_assignments_are_redacted():
    cases = [
        "token=abcd1234",
        'secret: "hunter2x"',
        "password = 'pa55word'",
        "api_key=sk-fake-12345",
        "API-KEY: zzzz9999",
    ]
    for case in cases:
        text, count = redact_text(case)
        assert count == 1, case
        assert REDACTED in text, case


def test_redacted_values_do_not_leak():
    text, _ = redact_text("api_key=sk-fake-12345 and token=abcd1234")
    assert "sk-fake-12345" not in text
    assert "abcd1234" not in text


def test_normal_text_is_not_redacted():
    cases = [
        "The token bucket algorithm limits request rates.",
        "Keep your password manager up to date.",
        "The secret to fast tests is isolation.",
        "Merge the pull request after CI passes.",
    ]
    for case in cases:
        text, count = redact_text(case)
        assert count == 0, case
        assert text == case


def test_redact_value_walks_nested_structures():
    value = {
        "overview": "token=abcd1234 leaked",
        "evidence": ["Bearer abcd1234efgh5678", "plain note"],
        "count": 3,
    }
    redacted, count = redact_value(value)
    assert count == 2
    assert "abcd1234" not in redacted["overview"]
    assert redacted["evidence"][0] == REDACTED
    assert redacted["evidence"][1] == "plain note"
    assert redacted["count"] == 3
