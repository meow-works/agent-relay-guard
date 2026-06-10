"""Input validation against the bundled JSON schema.

Validation is implemented with the standard library only and supports the
subset of JSON Schema used by ``schemas/input.schema.json``: ``type``
(object / string / array), ``const``, ``enum``, ``required``, ``properties``,
``additionalProperties: false``, ``items``, and ``minLength``. The schema file
remains the single source of truth for the input contract.
"""

import json
from importlib import resources

_SCHEMA_RESOURCE = "schemas/input.schema.json"


class ValidationError(Exception):
    """Raised when an input document does not satisfy the input schema."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def load_schema() -> dict:
    """Load the bundled input schema."""
    text = (
        resources.files("agent_relay_guard").joinpath(_SCHEMA_RESOURCE).read_text(encoding="utf-8")
    )
    return json.loads(text)


def schema_text() -> str:
    """Return the bundled input schema as raw JSON text."""
    return resources.files("agent_relay_guard").joinpath(_SCHEMA_RESOURCE).read_text(encoding="utf-8")


# JSON Schema keywords the hand-written validator understands. Annotation-only
# keywords ($schema, title, description) are listed because they are present in
# the schema file and intentionally carry no validation behavior. Any keyword
# in the schema outside this set would be silently ignored at runtime, so a
# development-time test (tests/test_validation.py) asserts none exist.
SUPPORTED_KEYWORDS = frozenset(
    {
        "$schema",
        "title",
        "description",
        "type",
        "const",
        "enum",
        "required",
        "properties",
        "additionalProperties",
        "items",
        "minLength",
    }
)


def unsupported_keywords(schema: dict) -> set[str]:
    """Return JSON Schema keywords used in ``schema`` that the validator ignores."""
    found: set[str] = set()

    def _walk(node: dict) -> None:
        for key, value in node.items():
            if key not in SUPPORTED_KEYWORDS:
                found.add(key)
            if key == "properties" and isinstance(value, dict):
                for sub_schema in value.values():
                    if isinstance(sub_schema, dict):
                        _walk(sub_schema)
            elif key == "items" and isinstance(value, dict):
                _walk(value)

    _walk(schema)
    return found


_TYPE_CHECKS = {
    "object": dict,
    "string": str,
    "array": list,
}

# Python types reported with JSON terminology in error messages.
_JSON_TYPE_NAMES = {
    dict: "object",
    list: "array",
    str: "string",
    bool: "boolean",
    int: "number",
    float: "number",
    type(None): "null",
}


def _json_type_name(value) -> str:
    return _JSON_TYPE_NAMES.get(type(value), type(value).__name__)


# User-controlled strings shown in error messages are escaped and truncated so
# that a hostile or accidental value (very long text, secret-like content,
# embedded newlines) cannot flood stderr or break its line structure.
_MAX_DISPLAY_LENGTH = 60


def _safe_display(value) -> str:
    """Render a user-controlled value for an error message.

    ``repr`` escapes control characters; long results are truncated.
    """
    text = repr(value)
    if len(text) > _MAX_DISPLAY_LENGTH:
        text = text[:_MAX_DISPLAY_LENGTH] + "...(truncated)"
    return text


def _safe_path_segment(key) -> str:
    """Render a user-controlled field name for use inside a JSON path."""
    escaped = "".join(
        ch if ch.isprintable() else ch.encode("unicode_escape").decode("ascii")
        for ch in str(key)
    )
    if len(escaped) > _MAX_DISPLAY_LENGTH:
        escaped = escaped[:_MAX_DISPLAY_LENGTH] + "...(truncated)"
    return escaped


def _check(value, schema: dict, path: str, errors: list[str]) -> None:
    if "const" in schema:
        if value != schema["const"]:
            errors.append(
                f"{path}: invalid value {_safe_display(value)}; the only supported value is "
                f"{schema['const']!r}"
            )
        return

    if "enum" in schema:
        if value not in schema["enum"]:
            allowed = ", ".join(repr(option) for option in schema["enum"])
            errors.append(
                f"{path}: invalid value {_safe_display(value)}; allowed values are: {allowed}"
            )
        return

    expected_type = schema.get("type")
    if expected_type is not None:
        python_type = _TYPE_CHECKS[expected_type]
        if not isinstance(value, python_type) or isinstance(value, bool):
            errors.append(f"{path}: expected {expected_type}, got {_json_type_name(value)}")
            return

    if expected_type == "string":
        min_length = schema.get("minLength", 0)
        if len(value) < min_length:
            errors.append(f"{path}: must not be shorter than {min_length} character(s)")
        return

    if expected_type == "array":
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                _check(item, item_schema, f"{path}[{index}]", errors)
        return

    if expected_type == "object":
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required field is missing")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}.{_safe_path_segment(key)}: unknown field")
        for key, sub_schema in properties.items():
            if key in value:
                _check(value[key], sub_schema, f"{path}.{key}", errors)


def validate_input(data) -> None:
    """Validate ``data`` against the input schema. Raise ValidationError on failure."""
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ValidationError(["$: input document must be a JSON object"])
    _check(data, load_schema(), "$", errors)
    if errors:
        raise ValidationError(errors)
