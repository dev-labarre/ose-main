"""
Compatibility module for extract_pipeline_v3_fast.

This module provides backward compatibility for notebooks that import
make_extract_pipeline_v3_fast from this module. The function is an alias
for make_extract_pipeline in extract_pipeline.py.
"""

from .extract_pipeline import make_extract_pipeline_v3_fast

__all__ = ["make_extract_pipeline_v3_fast"]
