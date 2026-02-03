"""
Command-line interface for GalacticNeighborsFinder.

Provides CLI tools for neighbor finding with customizable parameters
and configuration file support.
"""

import argparse
import sys
from pathlib import Path

from gnf.core.catalog import Catalog
from gnf.core.neighbor_finder import NeighborFinder
from gnf.config.config_loader import ConfigLoader
from gnf.utils.logger import setup_logger
from gnf.utils.validators import ValidationError
from gnf.constants import (
    RQE_COLUMN_MAPPING,
    SDSS_COLUMN_MAPPING,
    DEFAULT_MAX_NEIGHBORS,
    DEFAULT_R_PROJ_MAX_KPC,
    DEFAULT_VEL_DIFF_MAX_KMS,
)

logger = setup_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Find neighboring galaxies in astronomical catalogs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default parameters
  gnf-finder target.csv reference.csv output.csv
  
  # Custom search parameters
  gnf-finder target.csv reference.csv output.csv \\
    --max-neighbors 1000 --r-proj-max 10000 --vel-diff-max 5000
  
  # With configuration file
  gnf-finder --config config.yaml target.csv reference.csv output.csv
        """,
    )

    parser.add_argument("target_catalog", help="Path to target galaxy catalog (CSV)")
    parser.add_argument("reference_catalog", help="Path to reference galaxy catalog (CSV)")
    parser.add_argument("output_file", help="Path for output results (CSV)")

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="YAML configuration file with search parameters",
    )

    parser.add_argument(
        "--max-neighbors",
        type=int,
        default=DEFAULT_MAX_NEIGHBORS,
        help=f"Maximum neighbors per target (default: {DEFAULT_MAX_NEIGHBORS})",
    )

    parser.add_argument(
        "--r-proj-max",
        type=float,
        default=DEFAULT_R_PROJ_MAX_KPC,
        help=f"Maximum projected separation in kpc (default: {DEFAULT_R_PROJ_MAX_KPC})",
    )

    parser.add_argument(
        "--vel-diff-max",
        type=float,
        default=DEFAULT_VEL_DIFF_MAX_KMS,
        help=f"Maximum velocity difference in km/s (default: {DEFAULT_VEL_DIFF_MAX_KMS})",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Optional log file path",
    )

    args = parser.parse_args()

    # Reconfigure logger if specified
    if args.log_level or args.log_file:
        global logger
        logger = setup_logger(__name__, level=args.log_level, log_file=args.log_file)

    logger.info("GalacticNeighborsFinder started")

    try:
        # Load configuration if provided
        config = ConfigLoader(args.config) if args.config else ConfigLoader()

        # Override config with command-line arguments
        config.set("neighbor_search.max_neighbors", args.max_neighbors)
        config.set("neighbor_search.r_proj_max_kpc", args.r_proj_max)
        config.set("neighbor_search.vel_diff_max_kms", args.vel_diff_max)

        logger.info(f"Configuration: {config}")

        # Load catalogs
        logger.info(f"Loading target catalog: {args.target_catalog}")
        target_cat = Catalog(
            args.target_catalog,
            name="Target",
            column_mapping=config.get("catalogs.rqe.column_mapping"),
        )

        logger.info(f"Loading reference catalog: {args.reference_catalog}")
        reference_cat = Catalog(
            args.reference_catalog,
            name="Reference",
            column_mapping=config.get("catalogs.sdss.column_mapping"),
        )

        # Find neighbors
        logger.info("Initializing neighbor finder...")
        finder = NeighborFinder(target_cat, reference_cat)

        logger.info("Searching for neighbors...")
        results_df = finder.find_neighbors(
            max_neighbors=config.get("neighbor_search.max_neighbors"),
            r_proj_max=config.get("neighbor_search.r_proj_max_kpc"),
            vel_diff_max=config.get("neighbor_search.vel_diff_max_kms"),
        )

        # Save results
        if results_df.empty:
            logger.warning("No neighbors found. Writing empty output file.")
        else:
            results_df.to_csv(args.output_file, index=False)
            logger.info(f"Results saved to {args.output_file}")
            logger.info(f"Found {len(results_df)} total neighbors")
            logger.info(f"\nFirst 20 results:\n{results_df.head(20)}")

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

    logger.info("GalacticNeighborsFinder completed successfully")


if __name__ == "__main__":
    main()
