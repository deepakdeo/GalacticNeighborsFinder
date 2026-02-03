"""
Tests for validators module.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

from gnf.utils.validators import (
    ValidationError,
    validate_file_exists,
    validate_csv_format,
    validate_catalog_columns,
    validate_redshifts,
    validate_coordinates,
    validate_neighbor_parameters,
    validate_output_path,
)


class TestFileValidation:
    """Test file validation functions."""

    def test_validate_file_exists_valid(self, tmp_path):
        """Test validation passes for existing file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("data")
        assert validate_file_exists(str(test_file)) == test_file

    def test_validate_file_exists_missing(self):
        """Test validation fails for missing file."""
        with pytest.raises(ValidationError):
            validate_file_exists("/nonexistent/file.csv")

    def test_validate_csv_format_valid(self, tmp_path):
        """Test CSV validation passes for valid CSV."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("col1,col2\n1,2\n")
        validate_csv_format(str(test_file))  # Should not raise

    def test_validate_csv_format_empty(self, tmp_path):
        """Test CSV validation fails for empty file."""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("")
        with pytest.raises(ValidationError):
            validate_csv_format(str(test_file))


class TestCatalogValidation:
    """Test catalog validation functions."""

    def test_validate_columns_valid(self):
        """Test column validation passes with all required columns."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
        validate_catalog_columns(df, ["a", "b"])  # Should not raise

    def test_validate_columns_missing(self):
        """Test column validation fails with missing columns."""
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(ValidationError):
            validate_catalog_columns(df, ["a", "c"])


class TestRedshiftValidation:
    """Test redshift validation functions."""

    def test_validate_redshifts_valid(self):
        """Test redshift validation passes for valid values."""
        z = pd.Series([0.1, 0.5, 1.0, 2.0])
        validate_redshifts(z)  # Should not raise

    def test_validate_redshifts_too_low(self):
        """Test redshift validation fails for z < 0."""
        z = pd.Series([-0.1, 0.5])
        with pytest.raises(ValidationError):
            validate_redshifts(z)

    def test_validate_redshifts_too_high(self):
        """Test redshift validation fails for z > 10."""
        z = pd.Series([0.5, 15.0])
        with pytest.raises(ValidationError):
            validate_redshifts(z)


class TestCoordinateValidation:
    """Test coordinate validation functions."""

    def test_validate_coordinates_valid(self):
        """Test coordinate validation passes for valid ranges."""
        ra = pd.Series([0.0, 180.0, 359.9])
        dec = pd.Series([-89.9, 0.0, 89.9])
        validate_coordinates(ra, dec)  # Should not raise

    def test_validate_coordinates_ra_invalid(self):
        """Test coordinate validation fails for invalid RA."""
        ra = pd.Series([0.0, 361.0])
        dec = pd.Series([0.0, 0.0])
        with pytest.raises(ValidationError):
            validate_coordinates(ra, dec)

    def test_validate_coordinates_dec_invalid(self):
        """Test coordinate validation fails for invalid DEC."""
        ra = pd.Series([0.0, 0.0])
        dec = pd.Series([0.0, 91.0])
        with pytest.raises(ValidationError):
            validate_coordinates(ra, dec)


class TestNeighborParameters:
    """Test neighbor search parameter validation."""

    def test_validate_neighbor_parameters_valid(self):
        """Test parameter validation passes for valid values."""
        validate_neighbor_parameters(max_neighbors=500, r_proj_max=5000, vel_diff_max=3000)

    def test_validate_max_neighbors_invalid(self):
        """Test parameter validation fails for invalid max_neighbors."""
        with pytest.raises(ValidationError):
            validate_neighbor_parameters(max_neighbors=-1)

    def test_validate_r_proj_invalid(self):
        """Test parameter validation fails for invalid r_proj_max."""
        with pytest.raises(ValidationError):
            validate_neighbor_parameters(r_proj_max=-1)

    def test_validate_vel_diff_invalid(self):
        """Test parameter validation fails for invalid vel_diff_max."""
        with pytest.raises(ValidationError):
            validate_neighbor_parameters(vel_diff_max=-1)


class TestOutputPath:
    """Test output path validation."""

    def test_validate_output_path_valid(self, tmp_path):
        """Test output path validation passes for valid directory."""
        output_file = tmp_path / "output.csv"
        result = validate_output_path(str(output_file))
        assert result == output_file

    def test_validate_output_path_invalid_dir(self):
        """Test output path validation fails for nonexistent directory."""
        with pytest.raises(ValidationError):
            validate_output_path("/nonexistent/dir/output.csv")
