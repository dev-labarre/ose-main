"""
Configuration utilities for OSE.

Currently provides helpers for loading extraction settings used by the fast
pipeline. Config files live next to this module.
"""

from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml_config(config_name: str) -> Dict[str, Any]:
    """
    Load a YAML config file from this package.

    Parameters
    ----------
    config_name : str
        Name of the YAML file (e.g., 'extraction_config.yaml').

    Returns
    -------
    Dict[str, Any]
        Parsed configuration dictionary.
    """
    config_path = Path(__file__).parent / config_name
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)