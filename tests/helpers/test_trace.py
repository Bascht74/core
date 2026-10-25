"""Test the trace helper."""

from typing import Any

import pytest

from homeassistant.helpers.trace import TraceElement, trace_clear


class FailsWhenCompared:
    """Value that fails the test when the trace compares it."""

    def __eq__(self, other: object) -> bool:
        """Fail on any comparison."""
        raise AssertionError("value was compared")

    __hash__ = object.__hash__


@pytest.fixture(autouse=True)
def clear_trace() -> None:
    """Start every test without variables from a previous step."""
    trace_clear()


def test_same_object_is_not_compared() -> None:
    """A variable that still holds the same object is not reported again."""
    icons = FailsWhenCompared()
    TraceElement({"icons": icons}, "action/0")

    step = TraceElement({"icons": icons}, "action/1")

    assert "changed_variables" not in step.as_dict()


@pytest.mark.parametrize(
    ("second_step", "changed_variables"),
    [
        pytest.param({"rgb": [0, 0, 255]}, {"rgb": [0, 0, 255]}, id="changed_value"),
        pytest.param(
            {"rgb": [255, 0, 0], "brightness": 50},
            {"brightness": 50},
            id="new_variable",
        ),
        pytest.param({"rgb": [255, 0, 0]}, {}, id="equal_new_object"),
    ],
)
def test_changed_variables(
    second_step: dict[str, Any], changed_variables: dict[str, Any]
) -> None:
    """Only new variables and variables with a new value are reported."""
    # [255, 0, 0] is red, [0, 0, 255] is blue. Each case builds new lists,
    # so equality decides.
    TraceElement({"rgb": [255, 0, 0]}, "action/0")

    step = TraceElement(second_step, "action/1")

    assert step.as_dict().get("changed_variables", {}) == changed_variables
