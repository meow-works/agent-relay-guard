import copy
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def sample_input() -> dict:
    with open(EXAMPLES_DIR / "input" / "result.json", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture
def make_input(sample_input):
    """Return a deep copy of the sample input for mutation in tests."""

    def _make() -> dict:
        return copy.deepcopy(sample_input)

    return _make
