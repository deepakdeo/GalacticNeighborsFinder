import numpy as np
import pandas as pd
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u
from scipy.spatial import cKDTree as KDTree
from astropy.coordinates import SkyCoord
from tqdm import tqdm
import argparse

# Cosmological parameters for distance calculations
cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
C = 299792.458 * u.km / u.s  # Speed of light with units

def load_catalog(file_path):
    """
    Loads a galaxy catalog from a CSV file.
    
    Parameters:
        file_path (str): The path to the CSV file containing the galaxy catalog.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the galaxy catalog.
    
    Raises:
        Exception: If the file cannot be loaded.
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading catalog from {file_path}: {e}")
        raise

def convert_to_skycoord(catalog, ra_column, dec_column, z_column):
    """
    Converts catalog data to an Astropy SkyCoord object for astronomical calculations.
    
    Parameters:
        catalog (pandas.DataFrame): The galaxy catalog DataFrame.
        ra_column (str): Name of the column with right ascension data.
        dec_column (str): Name of the column with declination data.
        z_column (str): Name of the column with redshift data.
    
    Returns:
        astropy.coordinates.SkyCoord: A SkyCoord object representing the galaxy positions.
    """
    ra = catalog[ra_column].values * u.deg
    dec = catalog[dec_column].values * u.deg
    distance = cosmo.comoving_distance(catalog[z_column]).to(u.Mpc)
    return SkyCoord(ra=ra, dec=dec, distance=distance, frame='icrs')

def find_neighbors_and_compile_results(RQEcatalog, SDSScatalog, max_neighbors=500):
    """
    Finds neighboring galaxies within specified Rproj and velocity difference criteria
    and compiles the results into a DataFrame.
    
    Parameters:
        RQEcatalog (pandas.DataFrame): DataFrame of the RQE galaxy catalog.
        SDSScatalog (pandas.DataFrame): DataFrame of the SDSS galaxy catalog.
        max_neighbors (int): Maximum number of neighbors to consider.
    
    Returns:
        pandas.DataFrame: A DataFrame containing the compiled results with proximity scores.
    """
    RQE_coords = convert_to_skycoord(RQEcatalog, 'RAgal', 'DECgal', 'zgal')
    SDSS_coords = convert_to_skycoord(SDSScatalog, 'galaxy_ra_deg', 'galaxy_dec_deg', 'galaxy_z_CMB')

    tree = KDTree(np.vstack([SDSS_coords.cartesian.x.value, SDSS_coords.cartesian.y.value, SDSS_coords.cartesian.z.value]).T)
    results = []
    for i, rqe_coord in enumerate(tqdm(RQE_coords, desc="Processing RQE Catalog")):
        distances, indices = tree.query(rqe_coord.cartesian.xyz.value.T, k=max_neighbors)
        for dist, index in zip(distances, indices):
            if dist == 0:  # Skip self matches
                continue

            vel_diff = velocity_difference_from_redshift(RQEcatalog.iloc[i]['zgal'],
                                                         SDSScatalog.iloc[index]['galaxy_z_CMB']).value
            separation = rqe_coord.separation(SDSS_coords[index])

            if separation.arcminute <= 5000 and vel_diff <= 3000:  # Criteria check
                proximity_score = (separation.arcminute / 5000 + vel_diff / 3000) / 2
                combined_info = {
                    **RQEcatalog.iloc[i].to_dict(),
                    **SDSScatalog.iloc[index].to_dict(),
                    'velocity_diff_km_s': vel_diff,
                    'Rproj_kpc': separation.arcminute,
                    'proximity_score': proximity_score
                }
                results.append(combined_info)

    results_df = pd.DataFrame(results)
    # Ensure sorting by 'nyuID' and 'proximity_score' before ranking
    results_df.sort_values(by=['nyuID', 'proximity_score'], ascending=[True, True], inplace=True)

    # Apply neighbor rank based on proximity score within each RQE galaxy after sorting
    results_df['neighbor_rank'] = results_df.groupby('nyuID')['proximity_score'].rank(method='dense', ascending=True)

    return results_df

def velocity_difference_from_redshift(z1, z2):
    """
    Calculates the velocity difference based on redshifts.
    
    Parameters:
        z1 (float): Redshift of the first object.
        z2 (float): Redshift of the second object.
    
    Returns:
        float: Velocity difference in km/s.
    """
    return C * np.abs(z1 - z2)

def calculate_proximity_score(Rproj, vel_diff, R_max=5000, Delta_v_max=3000):
    """
    Calculates a normalized proximity score based on the projected radius (Rproj) and velocity difference (vel_diff).

    Parameters:
        Rproj (float): Projected radial distance between two galaxies.
        vel_diff (float): Velocity difference between two galaxies.
        R_max (float, optional): Maximum projected radius to normalize the data. Default is 5000.
        Delta_v_max (float, optional): Maximum velocity difference to normalize the data. Default is 3000.

    Returns:
        float: A normalized proximity score ranging from 0 to 1, where 0 indicates no proximity and 1 indicates maximum proximity.
    """
    N_Rproj = Rproj / R_max
    N_v_diff = vel_diff / Delta_v_max
    return 0.5 * N_Rproj + 0.5 * N_v_diff  # Equal weighting for simplicity

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process galaxy catalogs to find neighboring galaxies.")
    parser.add_argument('RQE_catalog_path', type=str, help='File path to the RQE galaxy catalog CSV file.')
    parser.add_argument('SDSS_catalog_path', type=str, help='File path to the SDSS galaxy catalog CSV file.')
    parser.add_argument('output_file_path', type=str, help='File path for saving the output CSV file.')
    parser.add_argument('--max_neighbors', type=int, default=500, help='Maximum number of neighbors to consider (default: 500).')
    parser.add_argument('--R_max', type=float, default=5000, help='Maximum projected physical separation cut in kpc (default: 5000).')
    parser.add_argument('--Delta_v_max', type=float, default=3000, help='Maximum velocity difference cut in km/s (default: 3000).')

    args = parser.parse_args()

    # Load the catalogs using provided file paths
    RQEcatalog = load_catalog(args.RQE_catalog_path)
    SDSScatalog = load_catalog(args.SDSS_catalog_path)

    # Find neighbors and compile results with additional parameters
    results_df = find_neighbors_and_compile_results(RQEcatalog, SDSScatalog, max_neighbors=args.max_neighbors)

    # Save the results to the specified output file path
    results_df.to_csv(args.output_file_path, index=False)
    print(f"Results saved to {args.output_file_path}")
    print(results_df.head(20))
