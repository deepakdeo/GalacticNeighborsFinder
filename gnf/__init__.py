"""
GalacticNeighborsFinder: Efficient neighbor identification in galaxy catalogs.

A Python package for identifying neighboring galaxies using k-d tree spatial
searches with cosmological calculations. Designed for efficient processing of
large astronomical catalogs with support for multiple catalog formats and
customizable search parameters.
"""

__version__ = "1.0.0"
__author__ = "Deepak Deo"
__license__ = "MIT"

from gnf.core.catalog import Catalog
from gnf.core.neighbor_finder import NeighborFinder, CosmologyCalculator
from gnf.config.config_loader import ConfigLoader
from gnf.utils.logger import setup_logger
from gnf.utils.validators import ValidationError

__all__ = [
    "Catalog",
    "NeighborFinder",
    "CosmologyCalculator",
    "ConfigLoader",
    "setup_logger",
    "ValidationError",
]
