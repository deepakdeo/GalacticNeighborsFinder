"""
Example: Using configuration files for reproducible analysis.

This example demonstrates how to use YAML configuration files to
manage search parameters and catalog settings.
"""

from gnf import ConfigLoader, Catalog, NeighborFinder, setup_logger

logger = setup_logger(__name__, level="INFO")


def main():
    """Run example with configuration file."""
    # Load configuration from YAML
    config = ConfigLoader("config_example.yaml")

    logger.info("Configuration loaded:")
    logger.info(config)

    # Get parameters from configuration
    max_neighbors = config.get("neighbor_search.max_neighbors")
    r_proj_max = config.get("neighbor_search.r_proj_max_kpc")
    vel_diff_max = config.get("neighbor_search.vel_diff_max_kms")

    rqe_mapping = config.get("catalogs.rqe.column_mapping")
    sdss_mapping = config.get("catalogs.sdss.column_mapping")

    logger.info(f"\nSearch parameters from config:")
    logger.info(f"  Max neighbors: {max_neighbors}")
    logger.info(f"  Projected distance limit: {r_proj_max} kpc")
    logger.info(f"  Velocity difference limit: {vel_diff_max} km/s")

    # Load catalogs with mappings from configuration
    rqe_catalog = Catalog(
        "path/to/rqe_catalog.csv",
        name="RQE",
        column_mapping=rqe_mapping,
    )

    sdss_catalog = Catalog(
        "path/to/sdss_catalog.csv",
        name="SDSS",
        column_mapping=sdss_mapping,
    )

    # Find neighbors using config parameters
    finder = NeighborFinder(rqe_catalog, sdss_catalog)
    results = finder.find_neighbors(
        max_neighbors=max_neighbors,
        r_proj_max=r_proj_max,
        vel_diff_max=vel_diff_max,
    )

    # Save results
    output_file = config.get("output.file_path", "results_from_config.csv")
    if not results.empty:
        results.to_csv(output_file, index=False)
        logger.info(f"Saved {len(results)} neighbors to {output_file}")


if __name__ == "__main__":
    main()
