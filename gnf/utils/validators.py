"""
Input validation utilities for GalacticNeighborsFinder.

Provides validation functions for catalog data, parameters, and file inputs.
"""

from typing import Any, List, Optional, Tuple
import pandas as pd
import os
from pathlib import Path

from gnf.constants import (
    MIN_REDSHIFT,
    MAX_REDSHIFT,
    MIN_VEL_DIFF_KMS,
    MAX_VEL_DIFF_KMS,
    MIN_SEPARATION_KPC,
    MAX_SEPARATION_KPC,
    DEFAULT_MAX_NEIGHBORS,
    DEFAULT_R_PROJ_MAX_KPC,
    DEFAULT_VEL_DIFF_MAX_KMS,
)


class ValidationError(Exception):
    """Custom exception for validation failures."""

    pass


def validate_file_exists(file_path: str) -> Path:
    """
    Validate that a file exists and is readable.

    Parameters
    ----------
    file_path : str
        Path to the file to validate.

    Returns
    -------
    Path
        Pathlib Path object if file is valid.

    Raises
    ------
    ValidationError
        If file does not exist or is not readable.
    """
    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")
    if not os.access(path, os.R_OK):
        raise ValidationError(f"File is not readable: {file_path}")
    return path


def validate_csv_format(file_path: str) -> None:
    """
    Validate that a file is a valid CSV.

    Parameters
    ----------
    file_path : str
        Path to the CSV file.

    Raises
    ------
    ValidationError
        If file cannot be read as CSV.
    """
    try:
        df = pd.read_csv(file_path, nrows=1)
        if df.empty:
            raise ValidationError(f"CSV file is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ValidationError(f"Invalid CSV format in {file_path}: {e}")
    except Exception as e:
        raise ValidationError(f"Error reading CSV file {file_path}: {e}")


def validate_catalog_columns(
    catalog: pd.DataFrame, required_columns: List[str], catalog_name: str = "Catalog"
) -> None:
    """
    Validate that catalog contains required columns.

    Parameters
    ----------
    catalog : pd.DataFrame
        The catalog DataFrame to validate.
    required_columns : List[str]
        List of required column names.
    catalog_name : str, optional
        Name of catalog for error messages (default: "Catalog").

    Raises
    ------
    ValidationError
        If any required columns are missing.
    """
    missing_cols = set(required_columns) - set(catalog.columns)
    if missing_cols:
        raise ValidationError(
            f"{catalog_name} missing required columns: {missing_cols}. "
            f"Available columns: {list(catalog.columns)}"
        )


def validate_redshifts(
    redshifts: pd.Series,
    min_z: float = MIN_REDSHIFT,
    max_z: float = MAX_REDSHIFT,
    name: str = "redshift",
) -> None:
    """
    Validate redshift values are within acceptable range.

    Parameters
    ----------
    redshifts : pd.Series
        Series of redshift values.
    min_z : float, optional
        Minimum acceptable redshift (default: MIN_REDSHIFT).
    max_z : float, optional
        Maximum acceptable redshift (default: MAX_REDSHIFT).
    name : str, optional
        Name of the redshift column for error messages (default: "redshift").

    Raises
    ------
    ValidationError
        If any redshift is outside valid range.
    """
    if (redshifts < min_z).any():
        raise ValidationError(
            f"{name} contains values below {min_z}. Found minimum: {redshifts.min()}"
        )
    if (redshifts > max_z).any():
        raise ValidationError(
            f"{name} contains values above {max_z}. Found maximum: {redshifts.max()}"
        )


def validate_coordinates(
    ra_values: pd.Series, dec_values: pd.Series
) -> None:
    """
    Validate RA/DEC coordinate ranges.

    Parameters
    ----------
    ra_values : pd.Series
        Right ascension values in degrees.
    dec_values : pd.Series
        Declination values in degrees.

    Raises
    ------
    ValidationError
        If coordinates are outside valid ranges.
    """
    if (ra_values < 0).any() or (ra_values > 360).any():
        raise ValidationError(
            f"RA values out of range [0, 360]. Found: [{ra_values.min()}, {ra_values.max()}]"
        )
    if (dec_values < -90).any() or (dec_values > 90).any():
        raise ValidationError(
            f"DEC values out of range [-90, 90]. Found: [{dec_values.min()}, {dec_values.max()}]"
        )


def validate_neighbor_parameters(
    max_neighbors: int = DEFAULT_MAX_NEIGHBORS,
    r_proj_max: float = DEFAULT_R_PROJ_MAX_KPC,
    vel_diff_max: float = DEFAULT_VEL_DIFF_MAX_KMS,
) -> None:
    """
    Validate neighbor search parameters.

    Parameters
    ----------
    max_neighbors : int, optional
        Maximum number of neighbors (default: DEFAULT_MAX_NEIGHBORS).
    r_proj_max : float, optional
        Maximum projected separation in kpc (default: DEFAULT_R_PROJ_MAX_KPC).
    vel_diff_max : float, optional
        Maximum velocity difference in km/s (default: DEFAULT_VEL_DIFF_MAX_KMS).

    Raises
    ------
    ValidationError
        If any parameter is invalid.
    """
    if max_neighbors <= 0:
        raise ValidationError(f"max_neighbors must be positive, got {max_neighbors}")

    if r_proj_max <= 0:
        raise ValidationError(f"r_proj_max must be positive, got {r_proj_max}")
    if r_proj_max > MAX_SEPARATION_KPC:
        raise ValidationError(
            f"r_proj_max too large: {r_proj_max} > {MAX_SEPARATION_KPC}"
        )

    if vel_diff_max <= 0:
        raise ValidationError(f"vel_diff_max must be positive, got {vel_diff_max}")
    if vel_diff_max > MAX_VEL_DIFF_KMS:
        raise ValidationError(
            f"vel_diff_max too large: {vel_diff_max} > {MAX_VEL_DIFF_KMS}"
        )


def validate_output_path(output_path: str) -> Path:
    """
    Validate that output path is writable.

    Parameters
    ----------
    output_path : str
        Path where output file will be written.

    Returns
    -------
    Path
        Pathlib Path object for the output file.

    Raises
    ------
    ValidationError
        If output directory doesn't exist or is not writable.
    """
    path = Path(output_path)
    parent_dir = path.parent

    if not parent_dir.exists():
        raise ValidationError(f"Output directory does not exist: {parent_dir}")
    if not os.access(parent_dir, os.W_OK):
        raise ValidationError(f"Output directory is not writable: {parent_dir}")

    return path
