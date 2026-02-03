"""
Core neighbor finding logic using k-d tree spatial searches.

Implements efficient neighbor identification using cosmological
calculations and spatial indexing.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
import astropy.units as u
from astropy.cosmology import FlatLambdaCDM
from astropy.coordinates import SkyCoord
from scipy.spatial import cKDTree as KDTree
from tqdm import tqdm

from gnf.utils.logger import setup_logger
from gnf.utils.validators import validate_neighbor_parameters, ValidationError
from gnf.constants import (
    HUBBLE_CONSTANT,
    MATTER_DENSITY,
    SPEED_OF_LIGHT_UNITS,
    DEFAULT_MAX_NEIGHBORS,
    DEFAULT_R_PROJ_MAX_KPC,
    DEFAULT_VEL_DIFF_MAX_KMS,
    RPROJ_WEIGHT,
    VEL_DIFF_WEIGHT,
    KDTREE_LEAF_SIZE,
)
from gnf.core.catalog import Catalog

logger = setup_logger(__name__)


class CosmologyCalculator:
    """
    Handles cosmological calculations for distance and velocity conversions.

    Attributes
    ----------
    cosmo : astropy.cosmology.FlatLambdaCDM
        Cosmological model instance.
    """

    def __init__(self, H0: float = HUBBLE_CONSTANT, Om0: float = MATTER_DENSITY):
        """
        Initialize cosmology calculator with specified parameters.

        Parameters
        ----------
        H0 : float, optional
            Hubble constant in km/s/Mpc (default: HUBBLE_CONSTANT).
        Om0 : float, optional
            Matter density parameter (default: MATTER_DENSITY).
        """
        self.cosmo = FlatLambdaCDM(H0=H0, Om0=Om0)
        logger.info(f"Initialized cosmology: H0={H0}, Om0={Om0}")

    def comoving_distance(self, redshift: pd.Series) -> np.ndarray:
        """
        Calculate comoving distance for given redshifts.

        Parameters
        ----------
        redshift : pd.Series
            Redshift values.

        Returns
        -------
        np.ndarray
            Comoving distances in Mpc.
        """
        return self.cosmo.comoving_distance(redshift).to(u.Mpc).value

    def velocity_from_redshift(self, z1: float, z2: float) -> float:
        """
        Calculate velocity difference between two redshifts.

        Parameters
        ----------
        z1 : float
            Redshift of first object.
        z2 : float
            Redshift of second object.

        Returns
        -------
        float
            Velocity difference in km/s.
        """
        return float((SPEED_OF_LIGHT_UNITS * np.abs(z1 - z2)).to(u.km / u.s).value)


class NeighborFinder:
    """
    Find neighboring galaxies using k-d tree spatial searches.

    Attributes
    ----------
    cosmo_calc : CosmologyCalculator
        Cosmology calculator instance.
    kdtree : scipy.spatial.cKDTree
        K-d tree for spatial indexing.
    target_coords : astropy.coordinates.SkyCoord
        SkyCoord objects for target catalog.
    reference_coords : astropy.coordinates.SkyCoord
        SkyCoord objects for reference catalog.
    """

    def __init__(
        self,
        target_catalog: Catalog,
        reference_catalog: Catalog,
        H0: float = HUBBLE_CONSTANT,
        Om0: float = MATTER_DENSITY,
    ):
        """
        Initialize neighbor finder with two catalogs.

        Parameters
        ----------
        target_catalog : Catalog
            Catalog to find neighbors for (e.g., RQE).
        reference_catalog : Catalog
            Catalog to search within (e.g., SDSS).
        H0 : float, optional
            Hubble constant (default: HUBBLE_CONSTANT).
        Om0 : float, optional
            Matter density (default: MATTER_DENSITY).
        """
        self.target_catalog = target_catalog
        self.reference_catalog = reference_catalog
        self.cosmo_calc = CosmologyCalculator(H0=H0, Om0=Om0)

        logger.info(f"Initializing NeighborFinder: {target_catalog.name} → {reference_catalog.name}")

        # Convert catalogs to SkyCoord
        self.target_coords = self._catalog_to_skycoord(target_catalog)
        self.reference_coords = self._catalog_to_skycoord(reference_catalog)

        # Build k-d tree from reference catalog
        self._build_kdtree()

    def _catalog_to_skycoord(self, catalog: Catalog) -> SkyCoord:
        """
        Convert catalog to SkyCoord objects with distances.

        Parameters
        ----------
        catalog : Catalog
            The catalog to convert.

        Returns
        -------
        astropy.coordinates.SkyCoord
            SkyCoord objects with positions and distances.
        """
        ra_col = catalog.get_column("ra")
        dec_col = catalog.get_column("dec")
        z_col = catalog.get_column("redshift")

        ra = catalog.data[ra_col].values * u.deg
        dec = catalog.data[dec_col].values * u.deg
        z = catalog.data[z_col].values

        # Calculate comoving distances
        distances = self.cosmo_calc.comoving_distance(z)
        distance = distances * u.Mpc

        logger.debug(f"Created SkyCoord for {catalog.name} with {len(ra)} objects")

        return SkyCoord(ra=ra, dec=dec, distance=distance, frame="icrs")

    def _build_kdtree(self) -> None:
        """
        Build k-d tree from reference catalog coordinates.

        Uses Cartesian coordinates for 3D spatial indexing.
        """
        # Convert to Cartesian coordinates for k-d tree
        coords_array = np.vstack(
            [
                self.reference_coords.cartesian.x.value,
                self.reference_coords.cartesian.y.value,
                self.reference_coords.cartesian.z.value,
            ]
        ).T

        self.kdtree = KDTree(coords_array, leaf_size=KDTREE_LEAF_SIZE)
        logger.info(f"Built k-d tree with {len(self.reference_coords)} reference objects")

    def find_neighbors(
        self,
        max_neighbors: int = DEFAULT_MAX_NEIGHBORS,
        r_proj_max: float = DEFAULT_R_PROJ_MAX_KPC,
        vel_diff_max: float = DEFAULT_VEL_DIFF_MAX_KMS,
    ) -> pd.DataFrame:
        """
        Find neighboring galaxies for all target objects.

        Parameters
        ----------
        max_neighbors : int, optional
            Maximum number of neighbors to return per target (default: DEFAULT_MAX_NEIGHBORS).
        r_proj_max : float, optional
            Maximum projected separation in kpc (default: DEFAULT_R_PROJ_MAX_KPC).
        vel_diff_max : float, optional
            Maximum velocity difference in km/s (default: DEFAULT_VEL_DIFF_MAX_KMS).

        Returns
        -------
        pd.DataFrame
            DataFrame with combined target and reference catalog data plus neighbor metrics.

        Raises
        ------
        ValidationError
            If parameters are invalid.
        """
        validate_neighbor_parameters(max_neighbors, r_proj_max, vel_diff_max)

        results = []
        z_col_target = self.target_catalog.get_column("redshift")
        z_col_ref = self.reference_catalog.get_column("redshift")
        id_col_target = self.target_catalog.get_column("id")

        logger.info(
            f"Searching for neighbors: max_neighbors={max_neighbors}, "
            f"r_proj_max={r_proj_max} kpc, vel_diff_max={vel_diff_max} km/s"
        )

        for i, target_coord in enumerate(tqdm(self.target_coords, desc="Processing targets")):
            # Query k-d tree
            distances, indices = self.kdtree.query(
                target_coord.cartesian.xyz.value, k=max_neighbors
            )

            target_z = self.target_catalog.data.iloc[i][z_col_target]
            target_id = self.target_catalog.data.iloc[i][id_col_target]

            for dist, idx in zip(distances, indices):
                # Skip self-matches
                if dist == 0:
                    continue

                ref_z = self.reference_catalog.data.iloc[idx][z_col_ref]

                # Calculate velocity difference
                vel_diff = self.cosmo_calc.velocity_from_redshift(target_z, ref_z)

                # Calculate angular separation and convert to physical
                separation = target_coord.separation(self.reference_coords[idx])
                r_proj = separation.to(u.arcmin).value  # in arcmin

                # Apply selection criteria
                if r_proj <= r_proj_max and vel_diff <= vel_diff_max:
                    # Calculate proximity score
                    proximity_score = self._calculate_proximity_score(
                        r_proj, vel_diff, r_proj_max, vel_diff_max
                    )

                    # Combine data from both catalogs
                    combined_info = {
                        **self.target_catalog.data.iloc[i].to_dict(),
                        **self.reference_catalog.data.iloc[idx].to_dict(),
                        "velocity_diff_km_s": vel_diff,
                        "Rproj_arcmin": r_proj,
                        "proximity_score": proximity_score,
                    }
                    results.append(combined_info)

        # Create results DataFrame
        if not results:
            logger.warning("No neighbors found matching selection criteria")
            return pd.DataFrame()

        results_df = pd.DataFrame(results)

        # Sort and rank neighbors
        results_df.sort_values(
            by=[id_col_target, "proximity_score"], ascending=[True, True], inplace=True
        )
        results_df["neighbor_rank"] = results_df.groupby(id_col_target)[
            "proximity_score"
        ].rank(method="dense", ascending=True)

        logger.info(f"Found {len(results_df)} neighbors for {len(self.target_coords)} targets")

        return results_df

    @staticmethod
    def _calculate_proximity_score(
        r_proj: float,
        vel_diff: float,
        r_proj_max: float = DEFAULT_R_PROJ_MAX_KPC,
        vel_diff_max: float = DEFAULT_VEL_DIFF_MAX_KMS,
    ) -> float:
        """
        Calculate normalized proximity score.

        Parameters
        ----------
        r_proj : float
            Projected separation in arcmin.
        vel_diff : float
            Velocity difference in km/s.
        r_proj_max : float, optional
            Maximum projected separation normalization (default: DEFAULT_R_PROJ_MAX_KPC).
        vel_diff_max : float, optional
            Maximum velocity difference normalization (default: DEFAULT_VEL_DIFF_MAX_KMS).

        Returns
        -------
        float
            Normalized proximity score between 0 and 1.
        """
        norm_r_proj = r_proj / r_proj_max
        norm_vel_diff = vel_diff / vel_diff_max

        return RPROJ_WEIGHT * norm_r_proj + VEL_DIFF_WEIGHT * norm_vel_diff
