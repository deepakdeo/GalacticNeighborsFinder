# GalacticNeighborsFinder

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Efficiently identify neighboring galaxies in astronomical catalogs using **k-d tree spatial searches** with full **cosmological support**. This Python package finds galaxies that match based on projected physical separation and velocity differences.

## Features

- **Efficient Spatial Search**: K-d tree algorithm for fast nearest-neighbor queries
- **Cosmological Calculations**: ΛCDM-based distance and velocity computations (Planck 2015)
- **Flexible Configuration**: YAML-based configuration system for reproducible analysis
- **Multiple Catalog Support**: Built-in mappings for RQE and SDSS; easily extensible
- **Comprehensive Validation**: Input validation for catalogs, parameters, and coordinates
- **Type Hints**: Full Python 3.8+ type annotations throughout
- **Logging Framework**: Professional logging with console and file output
- **Unit Tested**: 30+ comprehensive tests covering all modules
- **Well Documented**: Examples, API docs, and detailed docstrings

## Requirements

- **Python**: 3.8 or higher
- **Dependencies**: NumPy, Pandas, Astropy, SciPy, PyYAML, tqdm

## Installation

### From Source

```bash
# Clone repository
git clone https://github.com/deepakdeo/GalacticNeighborsFinder.git
cd GalacticNeighborsFinder

# Install package
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"
```

### Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install with conda
conda create -n gnf python=3.10
conda activate gnf
pip install -r requirements.txt
```

## Quick Start

### Command-Line Usage

```bash
# Basic usage with defaults
gnf-finder target_catalog.csv reference_catalog.csv results.csv

# Custom search parameters
gnf-finder target_catalog.csv reference_catalog.csv results.csv \
  --max-neighbors 1000 \
  --r-proj-max 10000 \
  --vel-diff-max 5000

# With configuration file
gnf-finder --config config.yaml target.csv reference.csv results.csv
```

### Python API

#### 1. Basic Neighbor Finding

```python
from gnf import Catalog, NeighborFinder
from gnf.constants import RQE_COLUMN_MAPPING, SDSS_COLUMN_MAPPING

# Load catalogs with column mappings
target = Catalog(
    "rqe_catalog.csv",
    name="RQE",
    column_mapping=RQE_COLUMN_MAPPING
)

reference = Catalog(
    "sdss_catalog.csv",
    name="SDSS",
    column_mapping=SDSS_COLUMN_MAPPING
)

# Find neighbors
finder = NeighborFinder(target, reference)
results = finder.find_neighbors(
    max_neighbors=500,      # Max neighbors per target
    r_proj_max=5000,        # Max projected distance (kpc)
    vel_diff_max=3000       # Max velocity difference (km/s)
)

# Save results
results.to_csv("neighbors.csv", index=False)
print(f"Found {len(results)} neighbors")
```

#### 2. Using Configuration Files

```python
from gnf import ConfigLoader, Catalog, NeighborFinder

# Load configuration
config = ConfigLoader("config.yaml")

# Get parameters from config
max_neighbors = config.get("neighbor_search.max_neighbors")
r_proj_max = config.get("neighbor_search.r_proj_max_kpc")

# Use config for catalogs and search
target = Catalog(
    "rqe_catalog.csv",
    column_mapping=config.get("catalogs.rqe.column_mapping")
)
reference = Catalog(
    "sdss_catalog.csv",
    column_mapping=config.get("catalogs.sdss.column_mapping")
)

finder = NeighborFinder(target, reference)
results = finder.find_neighbors(
    max_neighbors=max_neighbors,
    r_proj_max=r_proj_max,
    vel_diff_max=config.get("neighbor_search.vel_diff_max_kms")
)
```

#### 3. With Logging

```python
from gnf import setup_logger, NeighborFinder

# Set up logging
logger = setup_logger(
    __name__,
    level="INFO",
    log_file="search.log"
)

finder = NeighborFinder(target, reference)
logger.info("Starting neighbor search...")

results = finder.find_neighbors()
logger.info(f"Found {len(results)} neighbors")
```

## Project Structure

```
GalacticNeighborsFinder/
├── gnf/                          # Main package
│   ├── __init__.py              # Package initialization
│   ├── constants.py             # Global constants (cosmology, defaults)
│   ├── cli.py                   # Command-line interface
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── catalog.py           # Catalog loading and validation
│   │   └── neighbor_finder.py   # Neighbor finding algorithms
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── config_loader.py     # YAML configuration handler
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── logger.py            # Logging setup
│       └── validators.py        # Input validation
├── tests/                       # Unit tests (30+ tests)
├── examples/                    # Example scripts and configs
│   ├── example_basic.py         # Basic usage example
│   ├── example_config.py        # Config file example
│   └── config_example.yaml      # Example configuration
├── setup.py                     # Setup configuration
├── pyproject.toml              # Project metadata
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── README.md                   # This file
├── CONTRIBUTING.md             # Contribution guidelines
└── LICENSE                     # MIT License
```

## Configuration

Create a `config.yaml` file to customize your search:

```yaml
catalogs:
  rqe:
    column_mapping:
      ra: "RAgal"
      dec: "DECgal"
      redshift: "zgal"
      id: "nyuID"
  
  sdss:
    column_mapping:
      ra: "galaxy_ra_deg"
      dec: "galaxy_dec_deg"
      redshift: "galaxy_z_CMB"
      id: "objID"

neighbor_search:
  max_neighbors: 500
  r_proj_max_kpc: 5000
  vel_diff_max_kms: 3000

cosmology:
  H0: 70.0
  Om0: 0.3

logging:
  level: INFO
  log_file: null
```

See [examples/config_example.yaml](examples/config_example.yaml) for complete options.

## Module Overview

### gnf.core.catalog
- **Catalog**: Load and validate galaxy catalogs with column mapping
- Validates required columns (RA, DEC, redshift)
- Checks coordinate ranges and redshift validity

### gnf.core.neighbor_finder
- **CosmologyCalculator**: ΛCDM distance and velocity calculations (Planck 2015)
- **NeighborFinder**: Identify neighboring galaxies using k-d trees
  - 3D Cartesian coordinate indexing
  - Proximity scoring based on spatial and kinematic distance
  - Support for custom search parameters

### gnf.config.config_loader
- **ConfigLoader**: Load and manage YAML configurations
- Nested key access with dot notation
- Configuration merging and validation

### gnf.utils.validators
- Comprehensive validation functions:
  - File and CSV format checking
  - Catalog column validation
  - Redshift and coordinate range validation
  - Parameter bounds checking

### gnf.utils.logger
- Centralized logging with console and file output
- Consistent formatting across modules

## Output Format

Results include all columns from both catalogs plus:

| Column | Description |
|--------|-------------|
| `velocity_diff_km_s` | Velocity difference from redshift (km/s) |
| `Rproj_arcmin` | Projected angular separation (arcminutes) |
| `proximity_score` | Normalized proximity score [0, 1] |
| `neighbor_rank` | Neighbor rank by proximity (per target) |

## Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=gnf --cov-report=html

# Specific test file
pytest tests/test_neighbor_finder.py

# Verbose output
pytest -v
```

## API Reference

### Catalog

```python
from gnf import Catalog

catalog = Catalog(
    file_path: str,
    name: str = "Catalog",
    column_mapping: Optional[Dict[str, str]] = None
)
```

### NeighborFinder

```python
from gnf import NeighborFinder

finder = NeighborFinder(
    target_catalog: Catalog,
    reference_catalog: Catalog,
    H0: float = 70.0,
    Om0: float = 0.3
)

results = finder.find_neighbors(
    max_neighbors: int = 500,
    r_proj_max: float = 5000.0,
    vel_diff_max: float = 3000.0
) -> pd.DataFrame
```

### ConfigLoader

```python
from gnf import ConfigLoader

config = ConfigLoader(config_file: Optional[str] = None)

# Dot-notation access
value = config.get("section.subsection.key", default=None)

# Setting values
config.set("section.key", value)

# Export as dict
config_dict = config.to_dict()
```

## Examples

See [examples/](examples/) directory for:

- **example_basic.py**: Simple neighbor finding workflow
- **example_config.py**: Using YAML configuration files
- **config_example.yaml**: Complete configuration template

## Cosmological Parameters

The package uses Planck 2015 parameters by default:
- **H₀**: 70 km/s/Mpc
- **Ω_m**: 0.3 (matter density)
- **Ω_Λ**: 0.7 (dark energy)

Customize in configuration or when initializing:

```python
finder = NeighborFinder(target, reference, H0=67.4, Om0=0.315)
```

## Improvements from Original

✅ **Modular Architecture**: Organized into logical, reusable modules  
✅ **Type Hints**: Full Python 3.8+ annotations for IDE support  
✅ **Configuration System**: YAML-based configuration for reproducibility  
✅ **Input Validation**: Early error detection with informative messages  
✅ **Comprehensive Logging**: Professional logging throughout  
✅ **Unit Tests**: 30+ tests covering all functionality  
✅ **Better Documentation**: API docs, examples, and docstrings  
✅ **Error Handling**: Proper exception handling with validation errors  

## Troubleshooting

**Column not found error**
```
KeyError: Column 'RAgal' not found
```
Solution: Verify column names in your CSV and update `column_mapping`.

**Redshift validation error**
```
ValidationError: redshift contains values below 0.0
```
Solution: Check for negative or out-of-range redshift values in your catalog.

**No neighbors found**
```
No neighbors found matching selection criteria
```
Solution: Try increasing `r_proj_max` or `vel_diff_max` limits.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Development setup

## References

- **Cosmological Calculations**: Planck Collaboration et al. (2016) A&A 594, A13
- **K-d Trees**: Bentley, J. L. (1975) "Multidimensional binary search trees used for associative searching"
- **Astropy**: Astropy Collaboration et al. (2013) A&A 558, A33

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Authors

- **Deepak Deo**

## Citation

If you use GalacticNeighborsFinder in your research, please cite:

```bibtex
@software{deo_gnf_2024,
  author = {Deo, Deepak},
  title = {GalacticNeighborsFinder: Efficient neighbor identification in galaxy catalogs},
  url = {https://github.com/deepakdeo/GalacticNeighborsFinder},
  year = {2024}
}
```

---

*Version 1.0 (refactored) | Updated February 2026*
