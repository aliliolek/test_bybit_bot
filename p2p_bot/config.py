from __future__ import annotations

import os
from typing import Any, Dict

import yaml


def load_config(path: str) -> Dict[str, Any]:
    """Load YAML config and expand environment variables."""
    with open(path, "r", encoding="utf-8") as f:
        text = os.path.expandvars(f.read())
    data: Dict[str, Any] = yaml.safe_load(text) or {}
    return data
