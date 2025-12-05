"""
Fast extraction pipeline assembly.

This module wires loader and extractor components to produce the nine datasets
used throughout the OSE project. It is adapted from the v3.1 pipeline in
`_Data_Extract_Viz_agro` and keeps the dataframe format expected by
`DataLoader` (`src/ose_core/data`).
"""

from pathlib import Path
from typing import Dict, Iterator, Union

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from .extractors import (
    VectorizedArticleExtractor,
    VectorizedCompanyExtractor,
    VectorizedProjectExtractor,
)
from .loaders import FastJsonlLoader


class FastDatasetExtractor(BaseEstimator, TransformerMixin):
    """Extract datasets from DataFrame chunks using vectorized operations."""

    def __init__(self, file_type: str):
        """
        Parameters
        ----------
        file_type : str
            Type of file: 'company', 'article', or 'project'
        """
        self.file_type = file_type
        if file_type == "company":
            self.extractor = VectorizedCompanyExtractor()
        elif file_type == "article":
            self.extractor = VectorizedArticleExtractor()
        elif file_type == "project":
            self.extractor = VectorizedProjectExtractor()
        else:
            raise ValueError("file_type must be 'company', 'article', or 'project'")

    def fit(self, X, y=None):
        return self

    def transform(self, chunks: Iterator[pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Process a stream of chunks and return aggregated datasets."""
        chunk_count = 0
        total_records = 0

        for chunk_df in chunks:
            chunk_count += 1
            total_records += len(chunk_df)
            self.extractor.extract_chunk(chunk_df)
            if chunk_count % 10 == 0:
                print(f"  Processed {chunk_count} chunks ({total_records} records)...")

        print(f"Total chunks processed: {chunk_count}, Total records: {total_records}")
        datasets = self.extractor.get_datasets()
        return datasets


class DatasetCatalog(BaseEstimator, TransformerMixin):
    """Tidy and sort datasets for downstream EDA and modeling."""

    def fit(self, X, y=None):
        return self

    def transform(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Sort columns/index to keep a predictable schema."""
        result = {}
        for name, df in datasets.items():
            if not df.empty:
                index_cols = ["company_name", "siren", "siret"]
                other_cols = [c for c in df.columns if c not in index_cols]
                sorted_cols = [c for c in index_cols if c in df.columns] + sorted(other_cols)
                df = df[sorted_cols]
                df = df.reset_index(drop=True)
            result[name] = df
        return result


def make_extract_pipeline(
    file_paths: Dict[str, Union[str, Path]],
    chunk_size: int = 10000,
) -> Dict[str, pd.DataFrame]:
    """
    Run the fast extraction pipeline for company/article/project JSONL files.

    Parameters
    ----------
    file_paths : dict
        Mapping of file types to paths:
        {'company': path, 'article': path, 'project': path}
    chunk_size : int
        Number of lines to process per chunk (default: 10,000)

    Returns
    -------
    dict
        Dictionary with dataset names as keys and DataFrames as values.
        Keys: 01_company_basic_info ... 09_articles
    """
    all_datasets = []

    for file_type, file_path in file_paths.items():
        if file_path and Path(file_path).exists():
            print("\n" + "=" * 60)
            print(f"Processing {file_type} file: {file_path}")
            print("=" * 60)

            loader = FastJsonlLoader(chunk_size=chunk_size)
            extractor = FastDatasetExtractor(file_type=file_type)

            chunks = loader.transform({"jsonl_path": str(file_path)})
            datasets = extractor.transform(chunks)
            all_datasets.append(datasets)
        else:
            print(f"Warning: {file_type} file not found: {file_path}")

    merged: Dict[str, pd.DataFrame] = {}
    for datasets in all_datasets:
        for name, df in datasets.items():
            if name not in merged:
                merged[name] = []
            if not df.empty:
                merged[name].append(df)

    final_datasets: Dict[str, pd.DataFrame] = {}
    for name, df_list in merged.items():
        if df_list:
            final_datasets[name] = pd.concat(df_list, ignore_index=True)
        else:
            final_datasets[name] = pd.DataFrame()

    catalog = DatasetCatalog()
    final_datasets = catalog.transform(final_datasets)
    return final_datasets


def save_datasets_to_dir(datasets: Dict[str, pd.DataFrame], output_dir: Union[str, Path]) -> None:
    """
    Persist extracted datasets to disk as CSV files.

    Parameters
    ----------
    datasets : dict
        Dictionary of dataset name -> DataFrame.
    output_dir : str | Path
        Destination directory (will be created if missing).
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for name, df in datasets.items():
        csv_path = output_path / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        print(f"  wrote {csv_path} ({len(df)} rows)")


# Alias for backward compatibility with notebooks that import from extract_pipeline_v3_fast
make_extract_pipeline_v3_fast = make_extract_pipeline

