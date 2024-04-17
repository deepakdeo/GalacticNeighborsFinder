
# GalacticNeighborsFinder

This Python repository contains a script for identifying neighboring galaxies using data from astronomical catalogs. The script calculates proximity based on projected distance and velocity difference.

## Features
- Load galaxy catalogs from CSV files.
- Convert catalog data into Astropy `SkyCoord` objects for astronomical calculations.
- Find neighbors using criteria such as maximum neighbors, projected distance (Rproj), and velocity difference (vel_diff).
- Calculate a normalized proximity score based on specified criteria.

## Installation
Clone this repository to your local machine using:
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/GalacticNeighborsFinder.git
```
Ensure you have Python installed, along with the following packages: `numpy`, `pandas`, `astropy`, and `scipy`.

## Usage
1. Prepare your galaxy catalogs in CSV format.
2. Modify the file paths in the script to point to your catalog files.
3. Run the script:
   ```bash
   python paper2_NN_KDtree_fix_Rproj_vel_v2.py
   ```

## Example
Here's an example of loading a galaxy catalog and finding neighbors. In this specific example, I am attempting to identify all neighboring galaxies within specified criteria, by matching galaxies from the subset RQE catalog with those in the superset SDSS catalog:
```python
RQEcatalog = load_catalog('path_to_RQE_catalog.csv')
SDSScatalog = load_catalog('path_to_SDSS_catalog.csv')
results_df = find_neighbors_and_compile_results(RQEcatalog, SDSScatalog)
print(results_df.head(30))  # print first 30 rows of output file
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
