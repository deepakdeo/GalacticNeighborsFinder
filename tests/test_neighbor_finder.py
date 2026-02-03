"""
Tests for cosmology and neighbor finding.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile

from gnf.core.neighbor_finder import CosmologyCalculator, NeighborFinder
from gnf.core.catalog import Catalog
from gnf.utils.validators import ValidationError
from gnf.constants import RQE_COLUMN_MAPPING, SDSS_COLUMN_MAPPING


@pytest.fixture
def sample_catalogs(tmp_path):
    """Create sample catalogs for testing."""
    # Create target catalog (RQE-like)
    target_data = {
        "RAgal": [100.0, 150.0, 200.0],
        "DECgal": [20.0, 30.0, 40.0],
        "zgal": [0.1, 0.2, 0.3],
        "nyuID": [1, 2, 3],
        "flux": [1.5, 2.0, 1.8],
    }
    target_csv = tmp_path / "target.csv"
    pd.DataFrame(target_data).to_csv(target_csv, index=False)

    # Create reference catalog (SDSS-like)
    reference_data = {
        "galaxy_ra_deg": [100.5, 100.1, 150.2, 200.3],
        "galaxy_dec_deg": [20.5, 20.1, 30.2, 40.3],
        "galaxy_z_CMB": [0.09, 0.11, 0.19, 0.31],
        "objID": [101, 102, 103, 104],
        "magnitude": [18.5, 19.0, 17.8, 18.2],
    }
    reference_csv = tmp_path / "reference.csv"
    pd.DataFrame(reference_data).to_csv(reference_csv, index=False)

    return target_csv, reference_csv


class TestCosmologyCalculator:
    """Test cosmological calculations."""

    def test_init_default(self):
        """Test CosmologyCalculator initialization with defaults."""
        calc = CosmologyCalculator()
        assert calc.cosmo is not None

    def test_init_custom(self):
        """Test CosmologyCalculator initialization with custom parameters."""
        calc = CosmologyCalculator(H0=68, Om0=0.31)
        assert calc.cosmo is not None

    def test_comoving_distance(self):
        """Test comoving distance calculation."""
        calc = CosmologyCalculator(H0=70, Om0=0.3)
        z = pd.Series([0.1, 0.5, 1.0])
        distances = calc.comoving_distance(z)

        assert len(distances) == 3
        assert np.all(distances > 0)
        assert np.all(np.diff(distances) > 0)  # Monotonically increasing

    def test_velocity_from_redshift(self):
        """Test velocity difference from redshift."""
        calc = CosmologyCalculator()
        vel_diff = calc.velocity_from_redshift(0.1, 0.12)

        assert vel_diff > 0
        assert isinstance(vel_diff, float)

    def test_velocity_same_redshift(self):
        """Test velocity difference for same redshift."""
        calc = CosmologyCalculator()
        vel_diff = calc.velocity_from_redshift(0.1, 0.1)
        assert vel_diff == 0.0


class TestCatalog:
    """Test Catalog class."""

    def test_catalog_init_valid(self, sample_catalogs):
        """Test Catalog initialization with valid CSV."""
        target_csv, _ = sample_catalogs
        catalog = Catalog(str(target_csv), name="Test", column_mapping=RQE_COLUMN_MAPPING)

        assert catalog.name == "Test"
        assert len(catalog) == 3
        assert len(catalog.data) == 3

    def test_catalog_get_column(self, sample_catalogs):
        """Test column name mapping."""
        target_csv, _ = sample_catalogs
        catalog = Catalog(str(target_csv), column_mapping=RQE_COLUMN_MAPPING)

        assert catalog.get_column("ra") == "RAgal"
        assert catalog.get_column("dec") == "DECgal"
        assert catalog.get_column("redshift") == "zgal"

    def test_catalog_missing_required_column(self, tmp_path):
        """Test Catalog fails with missing required columns."""
        bad_data = {"col1": [1, 2, 3], "col2": [4, 5, 6]}
        bad_csv = tmp_path / "bad.csv"
        pd.DataFrame(bad_data).to_csv(bad_csv, index=False)

        with pytest.raises(ValidationError):
            Catalog(str(bad_csv), column_mapping=RQE_COLUMN_MAPPING)

    def test_catalog_invalid_redshift(self, tmp_path):
        """Test Catalog fails with invalid redshifts."""
        bad_data = {
            "RAgal": [100.0, 150.0],
            "DECgal": [20.0, 30.0],
            "zgal": [-0.1, 0.2],  # Negative redshift invalid
            "nyuID": [1, 2],
        }
        bad_csv = tmp_path / "bad_z.csv"
        pd.DataFrame(bad_data).to_csv(bad_csv, index=False)

        with pytest.raises(ValidationError):
            Catalog(str(bad_csv), column_mapping=RQE_COLUMN_MAPPING)


class TestNeighborFinder:
    """Test NeighborFinder class."""

    def test_neighbor_finder_init(self, sample_catalogs):
        """Test NeighborFinder initialization."""
        target_csv, reference_csv = sample_catalogs
        target_cat = Catalog(str(target_csv), name="Target", column_mapping=RQE_COLUMN_MAPPING)
        ref_cat = Catalog(
            str(reference_csv), name="Reference", column_mapping=SDSS_COLUMN_MAPPING
        )

        finder = NeighborFinder(target_cat, ref_cat)
        assert finder.kdtree is not None
        assert len(finder.target_coords) == 3
        assert len(finder.reference_coords) == 4

    def test_find_neighbors(self, sample_catalogs):
        """Test neighbor finding."""
        target_csv, reference_csv = sample_catalogs
        target_cat = Catalog(str(target_csv), name="Target", column_mapping=RQE_COLUMN_MAPPING)
        ref_cat = Catalog(
            str(reference_csv), name="Reference", column_mapping=SDSS_COLUMN_MAPPING
        )

        finder = NeighborFinder(target_cat, ref_cat)
        results = finder.find_neighbors(
            max_neighbors=10, r_proj_max=5000, vel_diff_max=3000
        )

        assert isinstance(results, pd.DataFrame)
        if not results.empty:
            assert "proximity_score" in results.columns
            assert "neighbor_rank" in results.columns
            assert "velocity_diff_km_s" in results.columns
            assert "Rproj_arcmin" in results.columns

    def test_proximity_score_calculation(self):
        """Test proximity score calculation."""
        score = NeighborFinder._calculate_proximity_score(
            r_proj=2500, vel_diff=1500, r_proj_max=5000, vel_diff_max=3000
        )

        assert 0 <= score <= 1
        assert score == 0.5  # (0.5 * 0.5) + (0.5 * 0.5) = 0.5

    def test_proximity_score_zero(self):
        """Test proximity score at origin."""
        score = NeighborFinder._calculate_proximity_score(
            r_proj=0, vel_diff=0, r_proj_max=5000, vel_diff_max=3000
        )
        assert score == 0.0

    def test_proximity_score_max(self):
        """Test proximity score at maximum."""
        score = NeighborFinder._calculate_proximity_score(
            r_proj=5000, vel_diff=3000, r_proj_max=5000, vel_diff_max=3000
        )
        assert score == 1.0

    def test_find_neighbors_strict_criteria(self, sample_catalogs):
        """Test neighbor finding with very strict criteria."""
        target_csv, reference_csv = sample_catalogs
        target_cat = Catalog(str(target_csv), name="Target", column_mapping=RQE_COLUMN_MAPPING)
        ref_cat = Catalog(
            str(reference_csv), name="Reference", column_mapping=SDSS_COLUMN_MAPPING
        )

        finder = NeighborFinder(target_cat, ref_cat)
        results = finder.find_neighbors(max_neighbors=10, r_proj_max=0.1, vel_diff_max=100)

        # With very strict criteria, likely to get empty result
        assert isinstance(results, pd.DataFrame)
