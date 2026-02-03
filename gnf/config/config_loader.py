"""
Configuration management for GalacticNeighborsFinder.

Provides YAML-based configuration loading and validation.
"""

from typing import Any, Dict, Optional
from pathlib import Path
import yaml

from gnf.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConfigLoader:
    """
    Load and manage YAML configuration files for neighbor finding.

    Attributes
    ----------
    config : Dict[str, Any]
        Configuration dictionary with nested key support via dot notation.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize ConfigLoader with optional configuration file.

        Parameters
        ----------
        config_file : str, optional
            Path to YAML configuration file.

        Raises
        ------
        FileNotFoundError
            If config_file is specified but not found.
        """
        self.config: Dict[str, Any] = self._get_default_config()

        if config_file:
            self.load(config_file)

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """
        Get default configuration values.

        Returns
        -------
        Dict[str, Any]
            Default configuration dictionary.
        """
        from gnf.constants import (
            DEFAULT_MAX_NEIGHBORS,
            DEFAULT_R_PROJ_MAX_KPC,
            DEFAULT_VEL_DIFF_MAX_KMS,
            RQE_COLUMN_MAPPING,
            SDSS_COLUMN_MAPPING,
        )

        return {
            "catalogs": {
                "rqe": {
                    "column_mapping": RQE_COLUMN_MAPPING,
                },
                "sdss": {
                    "column_mapping": SDSS_COLUMN_MAPPING,
                },
            },
            "neighbor_search": {
                "max_neighbors": DEFAULT_MAX_NEIGHBORS,
                "r_proj_max_kpc": DEFAULT_R_PROJ_MAX_KPC,
                "vel_diff_max_kms": DEFAULT_VEL_DIFF_MAX_KMS,
            },
            "output": {
                "format": "csv",
                "include_all_columns": True,
            },
            "logging": {
                "level": "INFO",
                "log_file": None,
            },
        }

    def load(self, config_file: str) -> None:
        """
        Load configuration from YAML file.

        Parameters
        ----------
        config_file : str
            Path to YAML configuration file.

        Raises
        ------
        FileNotFoundError
            If config file is not found.
        yaml.YAMLError
            If YAML parsing fails.
        """
        config_path = Path(config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f) or {}
            self._merge_configs(file_config)
            logger.info(f"Configuration loaded from {config_file}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {config_file}: {e}")

    def _merge_configs(self, new_config: Dict[str, Any]) -> None:
        """
        Recursively merge new configuration into existing configuration.

        Parameters
        ----------
        new_config : Dict[str, Any]
            Configuration dictionary to merge.
        """

        def merge_dict(base: Dict, update: Dict) -> None:
            for key, value in update.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value

        merge_dict(self.config, new_config)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Parameters
        ----------
        key_path : str
            Dot-separated path to configuration key (e.g., "neighbor_search.max_neighbors").
        default : Any, optional
            Default value if key is not found.

        Returns
        -------
        Any
            Configuration value or default if not found.

        Examples
        --------
        >>> config = ConfigLoader()
        >>> max_neighbors = config.get("neighbor_search.max_neighbors")
        >>> max_neighbors = config.get("nonexistent.key", default=100)
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Parameters
        ----------
        key_path : str
            Dot-separated path to configuration key.
        value : Any
            Value to set.

        Examples
        --------
        >>> config = ConfigLoader()
        >>> config.set("neighbor_search.max_neighbors", 1000)
        """
        keys = key_path.split(".")
        current = self.config

        # Navigate/create nested structure
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary.

        Returns
        -------
        Dict[str, Any]
            Complete configuration dictionary.
        """
        return self.config.copy()

    def __repr__(self) -> str:
        """Return string representation of configuration."""
        import json

        return json.dumps(self.config, indent=2)
