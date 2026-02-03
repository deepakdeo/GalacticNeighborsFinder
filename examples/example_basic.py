"""
Example: Basic neighbor finding with RQE and SDSS catalogs.

This example demonstrates how to use GalacticNeighborsFinder to identify
neighboring galaxies between two astronomical catalogs.
"""

from pathlib import Path

from gnf import Catalog, NeighborFinder, setup_logger
from gnf.constants import RQE_COLUMN_MAPPING, SDSS_COLUMN_MAPPING

# Set up logging
logger = setup_logger(__name__, level="INFO")


def main():
    """Run neighbor finding example."""
    # Paths to input catalogs (update these to your actual data)
    rqe_catalog_path = "path/to/rqe_catalog.csv"
    sdss_catalog_path = "path/to/sdss_catalog.csv"
    output_path = "neighbor_results.csv"

    logger.info("Starting neighbor finding example...")

    # Load catalogs with proper column mappings
    logger.info(f"Loading RQE catalog from {rqe_catalog_path}")
    rqe_catalog = Catalog(
        rqe_catalog_path,
        name="RQE",
        column_mapping=RQE_COLUMN_MAPPING,
    )

    logger.info(f"Loading SDSS catalog from {sdss_catalog_path}")
    sdss_catalog = Catalog(
        sdss_catalog_path,
        name="SDSS",
        column_mapping=SDSS_COLUMN_MAPPING,
    )

    # Create neighbor finder
    logger.info("Initializing neighbor finder...")
    finder = NeighborFinder(rqe_catalog, sdss_catalog)

    # Find neighbors with custom parameters
    logger.info("Searching for neighbors...")
    results = finder.find_neighbors(
        max_neighbors=500,  # Maximum neighbors per target
        r_proj_max=5000,     # Maximum projected separation (kpc)
        vel_diff_max=3000,   # Maximum velocity difference (km/s)
    )

    # Save and display results
    if results.empty:
        logger.warning("No neighbors found matching criteria")
    else:
        results.to_csv(output_path, index=False)
        logger.info(f"Saved {len(results)} neighbors to {output_path}")

        # Display statistics
        logger.info(f"\nResults summary:")
        logger.info(f"  Total neighbors found: {len(results)}")
        logger.info(f"  Targets with neighbors: {results['nyuID'].nunique()}")
        logger.info(f"  Proximity score range: [{results['proximity_score'].min():.3f}, "
                   f"{results['proximity_score'].max():.3f}]")
        logger.info(f"\nFirst 10 results:\n{results.head(10)}")


if __name__ == "__main__":
    main()
