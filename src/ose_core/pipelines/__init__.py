"""
Extraction pipelines for OSE.

This module exposes the fast extraction pipeline components used to build the
nine tabular datasets expected by `DataLoader` (`src/ose_core/data`).
"""

from .loaders import FastJsonlLoader
from .extractors import (
    VectorizedCompanyExtractor,
    VectorizedArticleExtractor,
    VectorizedProjectExtractor,
)
from .extract_pipeline import (
    FastDatasetExtractor,
    DatasetCatalog,
    make_extract_pipeline,
    make_extract_pipeline_v3_fast,
)

__all__ = [
    "FastJsonlLoader",
    "VectorizedCompanyExtractor",
    "VectorizedArticleExtractor",
    "VectorizedProjectExtractor",
    "FastDatasetExtractor",
    "DatasetCatalog",
    "make_extract_pipeline",
    "make_extract_pipeline_v3_fast",
]
