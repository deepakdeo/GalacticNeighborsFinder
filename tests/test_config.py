"""
Tests for configuration management.
"""

import pytest
import tempfile
from pathlib import Path

from gnf.config.config_loader import ConfigLoader
from gnf.constants import DEFAULT_MAX_NEIGHBORS, DEFAULT_R_PROJ_MAX_KPC


class TestConfigLoader:
    """Test configuration loading and management."""

    def test_init_default(self):
        """Test ConfigLoader initialization with defaults."""
        config = ConfigLoader()
        assert config.config is not None
        assert "neighbor_search" in config.config

    def test_get_default_value(self):
        """Test getting configuration value with dot notation."""
        config = ConfigLoader()
        max_neighbors = config.get("neighbor_search.max_neighbors")
        assert max_neighbors == DEFAULT_MAX_NEIGHBORS

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        config = ConfigLoader()
        ra_col = config.get("catalogs.rqe.column_mapping.ra")
        assert ra_col == "RAgal"

    def test_get_nonexistent_key(self):
        """Test getting nonexistent key returns None."""
        config = ConfigLoader()
        value = config.get("nonexistent.key")
        assert value is None

    def test_get_with_default(self):
        """Test getting value with default."""
        config = ConfigLoader()
        value = config.get("nonexistent.key", default=42)
        assert value == 42

    def test_set_value(self):
        """Test setting configuration value."""
        config = ConfigLoader()
        config.set("neighbor_search.max_neighbors", 1000)
        assert config.get("neighbor_search.max_neighbors") == 1000

    def test_set_nested_value(self):
        """Test setting deeply nested value."""
        config = ConfigLoader()
        config.set("custom.deep.nested.value", "test")
        assert config.get("custom.deep.nested.value") == "test"

    def test_to_dict(self):
        """Test exporting configuration as dictionary."""
        config = ConfigLoader()
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "neighbor_search" in config_dict

    def test_load_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        yaml_content = """
neighbor_search:
  max_neighbors: 2000
  r_proj_max_kpc: 10000
output:
  format: csv
        """
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        config = ConfigLoader(str(yaml_file))
        assert config.get("neighbor_search.max_neighbors") == 2000
        assert config.get("neighbor_search.r_proj_max_kpc") == 10000
        assert config.get("output.format") == "csv"

    def test_load_yaml_merge_defaults(self, tmp_path):
        """Test that YAML loading merges with defaults."""
        yaml_content = """
neighbor_search:
  max_neighbors: 750
        """
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        config = ConfigLoader(str(yaml_file))
        # Custom value should be loaded
        assert config.get("neighbor_search.max_neighbors") == 750
        # Default value should still be present
        assert config.get("neighbor_search.r_proj_max_kpc") == DEFAULT_R_PROJ_MAX_KPC

    def test_load_invalid_yaml(self, tmp_path):
        """Test that invalid YAML raises error."""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("invalid: yaml: content::")

        with pytest.raises(Exception):  # yaml.YAMLError
            ConfigLoader(str(yaml_file))

    def test_load_missing_file(self):
        """Test that missing file raises error."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader("/nonexistent/config.yaml")

    def test_repr(self):
        """Test configuration string representation."""
        config = ConfigLoader()
        repr_str = repr(config)
        assert isinstance(repr_str, str)
        assert "neighbor_search" in repr_str
