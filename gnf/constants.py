"""
Global constants for GalacticNeighborsFinder package.

This module centralizes all constants used throughout the application,
including cosmological parameters, default configuration values, and
physical constants.
"""

import astropy.units as u

# ==============================================================================
# COSMOLOGICAL PARAMETERS
# ==============================================================================

HUBBLE_CONSTANT: float = 70.0  # km/s/Mpc
MATTER_DENSITY: float = 0.3  # Omega_m
DARK_ENERGY_DENSITY: float = 0.7  # Omega_Lambda
MATTER_POWER_INDEX: float = 0.0  # Flat ΛCDM

# ==============================================================================
# PHYSICAL CONSTANTS
# ==============================================================================

SPEED_OF_LIGHT: float = 299792.458  # km/s
SPEED_OF_LIGHT_UNITS: u.Quantity = SPEED_OF_LIGHT * u.km / u.s

# ==============================================================================
# COORDINATE CONVENTIONS
# ==============================================================================

# Default coordinate column names in catalogs
DEFAULT_RA_COLUMN: str = "RA"
DEFAULT_DEC_COLUMN: str = "DEC"
DEFAULT_REDSHIFT_COLUMN: str = "z"

# Common survey-specific column mappings
RQE_COLUMN_MAPPING = {
    "ra": "RAgal",
    "dec": "DECgal",
    "redshift": "zgal",
    "id": "nyuID",
}

SDSS_COLUMN_MAPPING = {
    "ra": "galaxy_ra_deg",
    "dec": "galaxy_dec_deg",
    "redshift": "galaxy_z_CMB",
    "id": "objID",
}

# ==============================================================================
# NEIGHBOR SEARCH PARAMETERS
# ==============================================================================

# Default neighbor search constraints
DEFAULT_MAX_NEIGHBORS: int = 500
DEFAULT_R_PROJ_MAX_KPC: float = 5000.0  # Maximum projected physical separation (kpc)
DEFAULT_VEL_DIFF_MAX_KMS: float = 3000.0  # Maximum velocity difference (km/s)

# Angular separation thresholds (for initial filtering)
MIN_ANGULAR_SEPARATION_ARCMIN: float = 0.0
MAX_ANGULAR_SEPARATION_ARCMIN: float = 10.0  # Conservative upper limit

# ==============================================================================
# VALIDATION RANGES
# ==============================================================================

# Redshift ranges
MIN_REDSHIFT: float = 0.0
MAX_REDSHIFT: float = 10.0

# Velocity difference ranges
MIN_VEL_DIFF_KMS: float = 0.0
MAX_VEL_DIFF_KMS: float = 100000.0  # ~0.33c

# Physical separation ranges
MIN_SEPARATION_KPC: float = 0.0
MAX_SEPARATION_KPC: float = 100000.0  # ~Megaparsec scale

# ==============================================================================
# PROXIMITY SCORE PARAMETERS
# ==============================================================================

# Weight factors for proximity score calculation
RPROJ_WEIGHT: float = 0.5
VEL_DIFF_WEIGHT: float = 0.5

# Ensure weights sum to 1.0
assert abs(RPROJ_WEIGHT + VEL_DIFF_WEIGHT - 1.0) < 1e-9, "Proximity score weights must sum to 1.0"

# ==============================================================================
# OUTPUT/LOGGING
# ==============================================================================

# Output file defaults
DEFAULT_OUTPUT_FORMAT: str = "csv"
OUTPUT_FLOAT_PRECISION: int = 6

# Logging levels
DEFAULT_LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==============================================================================
# PROCESSING PARAMETERS
# ==============================================================================

# Batch processing settings
DEFAULT_BATCH_SIZE: int = 1000
PROGRESS_BAR_ENABLED: bool = True

# K-d tree parameters
KDTREE_METRIC: str = "euclidean"
KDTREE_LEAF_SIZE: int = 30

# ==============================================================================
# COLUMN NAMES FOR OUTPUT
# ==============================================================================

OUTPUT_COLUMNS_ADDED = [
    "velocity_diff_km_s",
    "Rproj_kpc",
    "proximity_score",
    "neighbor_rank",
]
