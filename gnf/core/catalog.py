"""
Catalog loading and manipulation utilities.

Handles loading galaxy catalogs from various formats and performing
basic preprocessing and validation.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

from gnf.utils.logger import setup_logger
from gnf.utils.validators import (
    validate_file_exists,
    validate_csv_format,
    validate_catalog_columns,
    validate_redshifts,
    validate_coordinates,
    ValidationError,
)

logger = setup_logger(__name__)


class Catalog:
    """
    Represents a galaxy catalog with validation and preprocessing.

    Attributes
    ----------
    data : pd.DataFrame
        The catalog data.
    name : str
        Catalog identifier/name.
    column_mapping : Dict[str, str]
        Mapping of standard names to actual column names.
    """

    def __init__(
        self,
        file_path: str,
        name: str = "Catalog",
        column_mapping: Optional[Dict[str, str]] = None,
    ):
        """
        Load and initialize a catalog.

        Parameters
        ----------
        file_path : str
            Path to the catalog CSV file.
        name : str, optional
            Catalog name for logging (default: "Catalog").
        column_mapping : Dict[str, str], optional
            Mapping of standard columns to actual column names.
            Keys: 'ra', 'dec', 'redshift', 'id'

        Raises
        ------
        ValidationError
            If file validation fails or required columns are missing.
        """
        self.name = name
        self.column_mapping = column_mapping or {}

        # Validate and load file
        validate_file_exists(file_path)
        validate_csv_format(file_path)

        try:
            self.data = pd.read_csv(file_path)
            logger.info(f"Loaded {name} with {len(self.data)} objects from {file_path}")
        except Exception as e:
            raise ValidationError(f"Failed to load catalog from {file_path}: {e}")

        # Validate structure
        self._validate_catalog()

    def _validate_catalog(self) -> None:
        """
        Validate catalog has required columns and valid data.

        Raises
        ------
        ValidationError
            If validation fails.
        """
        required_cols = ["ra", "dec", "redshift"]
        actual_cols = [self.column_mapping.get(col, col) for col in required_cols]

        validate_catalog_columns(self.data, actual_cols, self.name)

        # Validate coordinate ranges
        ra_col = self.column_mapping.get("ra", "ra")
        dec_col = self.column_mapping.get("dec", "dec")
        z_col = self.column_mapping.get("redshift", "redshift")

        try:
            validate_coordinates(self.data[ra_col], self.data[dec_col])
            validate_redshifts(self.data[z_col], name=f"{self.name} redshift column")
            logger.info(f"{self.name} validation passed")
        except ValidationError as e:
            logger.error(f"{self.name} validation failed: {e}")
            raise

    def get_column(self, standard_name: str) -> str:
        """
        Get actual column name for a standard column name.

        Parameters
        ----------
        standard_name : str
            Standard column name ('ra', 'dec', 'redshift', 'id').

        Returns
        -------
        str
            Actual column name in the catalog.

        Raises
        ------
        KeyError
            If standard name is not in mapping and not in data.
        """
        actual_name = self.column_mapping.get(standard_name, standard_name)
        if actual_name not in self.data.columns:
            raise KeyError(
                f"Column '{actual_name}' not found in {self.name}. "
                f"Available columns: {list(self.data.columns)}"
            )
        return actual_name

    def __len__(self) -> int:
        """Return number of objects in catalog."""
        return len(self.data)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Catalog(name='{self.name}', objects={len(self)})"
