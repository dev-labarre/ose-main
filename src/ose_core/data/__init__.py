"""
OSE Data Module

Provides DataLoader class for loading datasets from extracted_datasets folder.
"""
from pathlib import Path
import pandas as pd
from typing import Dict, Optional


class DataLoader:
    """
    DataLoader class for loading datasets from the extracted_datasets directory.
    
    Handles path resolution and provides methods to load individual or all datasets.
    """
    
    def __init__(self):
        """Initialize DataLoader with path to data directory."""
        self._data_dir = self._get_data_dir()
        self._extracted_datasets_dir = self._data_dir / "extracted_datasets"
    
    def _get_data_dir(self) -> Path:
        """
        Get the path to the data directory (src/ose_core/data/).
        
        Uses __file__ to resolve the path relative to this module.
        """
        # Get the directory where this __init__.py file is located
        return Path(__file__).parent
    
    def get_data_dir(self) -> Path:
        """
        Returns the Path to src/ose_core/data/ directory.
        
        Returns:
            Path: Path object pointing to the data directory
        """
        return self._data_dir
    
    def get_extracted_datasets_dir(self) -> Path:
        """
        Returns the Path to extracted_datasets/ subdirectory.
        
        Returns:
            Path: Path object pointing to the extracted_datasets directory
        """
        return self._extracted_datasets_dir
    
    def load_dataset(self, name: str) -> pd.DataFrame:
        """
        Load a specific dataset by name.
        
        Args:
            name: Dataset name (e.g., '01_company_basic_info', '02_financial_data')
                  Can be with or without the .csv extension
        
        Returns:
            pd.DataFrame: Loaded dataset as a pandas DataFrame
        
        Raises:
            FileNotFoundError: If the dataset file doesn't exist
        """
        # Remove .csv extension if present
        if name.endswith('.csv'):
            name = name[:-4]
        
        csv_path = self._extracted_datasets_dir / f"{name}.csv"
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {csv_path}")
        
        return pd.read_csv(csv_path)
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all 9 datasets from the extracted_datasets directory.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping dataset names to DataFrames
            Format: {'01_company_basic_info': DataFrame, '02_financial_data': DataFrame, ...}
        """
        datasets = {}
        
        # Expected dataset names
        expected_datasets = [
            '01_company_basic_info',
            '02_financial_data',
            '03_workforce_data',
            '04_company_structure',
            '05_classification_flags',
            '06_contact_metrics',
            '07_kpi_data',
            '08_signals',
            '09_articles'
        ]
        
        for dataset_name in expected_datasets:
            csv_path = self._extracted_datasets_dir / f"{dataset_name}.csv"
            
            if csv_path.exists():
                datasets[dataset_name] = pd.read_csv(csv_path)
            else:
                # If CSV doesn't exist, try JSON as fallback
                json_path = self._extracted_datasets_dir / f"{dataset_name}.json"
                if json_path.exists():
                    datasets[dataset_name] = pd.read_json(json_path)
                else:
                    raise FileNotFoundError(
                        f"Dataset file not found: {dataset_name} "
                        f"(checked {csv_path} and {json_path})"
                    )
        
        return datasets
    
    def get_raw_json_path(self) -> Optional[Path]:
        """
        Get the path to the raw JSON file if it exists.
        
        Returns:
            Optional[Path]: Path to search_24721_2025_11_24.json if it exists, None otherwise
        """
        json_path = self._data_dir / "search_24721_2025_11_24.json"
        return json_path if json_path.exists() else None

