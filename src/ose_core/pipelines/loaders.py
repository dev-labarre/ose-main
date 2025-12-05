"""
Data loading utilities for extraction pipelines.

Provides a fast JSONL loader that streams data in chunks using pandas'
native JSON reader. This mirrors the behavior of the v3.1 pipeline from
`_Data_Extract_Viz_agro`.
"""

from pathlib import Path
from typing import Dict, Iterator

import pandas as pd


class FastJsonlLoader:
    """Load JSONL files in chunks using pandas' native reader."""

    def __init__(self, chunk_size: int = 10000) -> None:
        """
        Parameters
        ----------
        chunk_size : int
            Number of lines to process per chunk (default: 10,000)
        """
        self.chunk_size = chunk_size

    def transform(self, params: Dict[str, str]) -> Iterator[pd.DataFrame]:
        """
        Stream JSONL data in chunks.

        Parameters
        ----------
        params : dict
            Dictionary containing 'jsonl_path' key with path to JSONL file.

        Yields
        ------
        pd.DataFrame
            Chunks of records as DataFrames (with `_source` extracted if in
            Elasticsearch format).
        """
        jsonl_path = params.get("jsonl_path")
        if not jsonl_path:
            raise ValueError("params must contain 'jsonl_path' key")

        jsonl_path = Path(jsonl_path)
        if not jsonl_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")

        print(f"Loading data from {jsonl_path} in chunks of {self.chunk_size}...")

        chunk_reader = pd.read_json(
            jsonl_path,
            lines=True,
            chunksize=self.chunk_size,
            orient="records",
        )

        total_lines = 0
        for chunk_num, chunk_df in enumerate(chunk_reader):
            total_lines += len(chunk_df)

            # Extract _source if it's Elasticsearch format
            if "_source" in chunk_df.columns:
                if chunk_df["_source"].dtype == "object":
                    source_list = chunk_df["_source"].tolist()
                    # Normalize nested JSON structures, preserving all columns
                    try:
                        source_df = pd.json_normalize(source_list)
                        # If normalization succeeded, use the normalized dataframe
                        chunk_df = source_df
                    except Exception as e:
                        # Fallback: try to extract _source manually if normalization fails
                        # This handles cases where _source contains complex nested structures
                        extracted_sources = []
                        for source_val in source_list:
                            if isinstance(source_val, dict):
                                extracted_sources.append(source_val)
                            elif pd.notna(source_val):
                                extracted_sources.append(source_val)
                        if extracted_sources:
                            chunk_df = pd.DataFrame(extracted_sources)
                        else:
                            chunk_df = chunk_df.drop(columns=["_source"], errors="ignore")
                else:
                    chunk_df = chunk_df.drop(columns=["_source"], errors="ignore")
            
            # Ensure we have a valid dataframe with at least one row
            if len(chunk_df) == 0:
                continue

            if (chunk_num + 1) % 10 == 0:
                print(f"  Processed {total_lines} lines...")

            yield chunk_df

        print(f"Total lines loaded: {total_lines}")

