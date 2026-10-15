"""Numbers shown in the exercise windows, with the Portuguese decimal comma."""

from __future__ import annotations


def numero(value: float, spec: str) -> str:
    """Format `value` with a format spec (".2f", "+.1f", ".1%") and a decimal comma: 0.25 -> "0,25"."""
    return format(value, spec).replace(".", ",")
