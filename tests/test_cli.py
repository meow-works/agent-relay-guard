import json
import os
import subprocess
import sys

import pytest

from conftest import EXAMPLES_DIR, SRC_DIR

SAMPLE_INPUT = EXAMPLES_DIR / "input" / "result.json"


def run_cli(*args, cwd=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_DIR)
    return subprocess.run(
        [sys.executable, "-m", "agent_relay_guard.cli", *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
    )


@pytest.mark.parametrize("input_name", ["result.json", "progress.json"])
def test_validate_valid_input_exits_zero(input_name):
    result = run_cli("validate", str(EXAMPLES_DIR / "input" / input_name))
    assert result.returncode == 0
    assert "valid" in result.stdout


def test_validate_invalid_json_exits_one(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = run_cli("validate", str(bad))
    assert result.returncode == 1
    assert "error" in result.stderr


def test_validate_schema_violation_exits_one(tmp_path):
    data = json.loads(SAMPLE_INPUT.read_text(encoding="utf-8"))
    data["risk"] = "severe"
    bad = tmp_path / "bad_enum.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    result = run_cli("validate", str(bad))
    assert result.returncode == 1


def test_missing_input_file_exits_two(tmp_path):
    result = run_cli("validate", str(tmp_path / "does_not_exist.json"))
    assert result.returncode == 2
    assert "error" in result.stderr


def test_usage_error_exits_two():
    assert run_cli().returncode == 2
    assert run_cli("render", str(SAMPLE_INPUT), "--format", "yaml").returncode == 2


def test_unwritable_output_exits_two(tmp_path):
    target = tmp_path / "no_such_dir" / "card.md"
    result = run_cli("render", str(SAMPLE_INPUT), "--output", str(target))
    assert result.returncode == 2


def test_render_markdown_to_stdout():
    result = run_cli("render", str(SAMPLE_INPUT))
    assert result.returncode == 0
    assert result.stdout.startswith("# Fix flaky timing test in parser module (task-042)")


def test_render_json_to_output_file(tmp_path):
    target = tmp_path / "card.json"
    result = run_cli("render", str(SAMPLE_INPUT), "--format", "json", "--output", str(target))
    assert result.returncode == 0
    card = json.loads(target.read_text(encoding="utf-8"))
    assert card["detail_packet_id"] == "task-042-detail"
    assert card["redaction_count"] == 0
    assert card["options"] == ["APPROVE", "HOLD", "REJECT", "REVISE"]
    assert "overview" not in card


def test_detail_json_to_stdout():
    result = run_cli("detail", str(SAMPLE_INPUT), "--format", "json")
    assert result.returncode == 0
    packet = json.loads(result.stdout)
    assert packet["detail_packet_id"] == "task-042-detail"
    assert packet["redaction_count"] == 0
    assert packet["evidence"]


def test_schema_command_prints_valid_json():
    result = run_cli("schema")
    assert result.returncode == 0
    schema = json.loads(result.stdout)
    assert schema["properties"]["schema_version"]["const"] == "1.0"


@pytest.mark.parametrize("input_name", ["result", "progress"])
@pytest.mark.parametrize(
    ("args", "golden_suffix"),
    [
        (("render", "--format", "markdown"), "card.md"),
        (("render", "--format", "json"), "card.json"),
        (("detail", "--format", "json"), "detail.json"),
        (("detail", "--format", "markdown"), "detail.md"),
    ],
)
def test_golden_outputs_match_examples(input_name, args, golden_suffix):
    command, *flags = args
    input_path = EXAMPLES_DIR / "input" / f"{input_name}.json"
    result = run_cli(command, str(input_path), *flags)
    assert result.returncode == 0
    golden = EXAMPLES_DIR / "output" / f"{input_name}.{golden_suffix}"
    assert result.stdout == golden.read_text(encoding="utf-8")
