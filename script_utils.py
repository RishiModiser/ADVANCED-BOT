"""Validation helpers for JSON RPA script documents."""

from typing import Any, Dict, List


def validate_rpa_script_data(data: Any) -> None:
    """Validate the structure accepted by the RPA script normalizer.

    A script may be a single step object, a list of steps, or an object
    containing a ``steps`` list. Detailed action-specific validation remains
    in the existing normalizer and executor.
    """
    if isinstance(data, list):
        steps = data
    elif isinstance(data, dict):
        steps = data.get("steps", [data])
        if not isinstance(steps, list):
            raise ValueError("RPA script 'steps' must be a list")
    else:
        raise ValueError("RPA script must be a JSON object or array")

    for index, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            raise ValueError(f"RPA step {index} must be an object")
        if not isinstance(step.get("type"), str) or not step["type"].strip():
            raise ValueError(f"RPA step {index} must define a non-empty 'type'")
