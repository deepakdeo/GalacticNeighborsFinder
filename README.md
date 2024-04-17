
# GalacticNeighborsFinder

This Python repository contains a script for identifying neighboring galaxies using data from astronomical catalogs. The script employs the k-d tree algorithm, a sophisticated data structure commonly used in machine learning for efficiently handling nearest-neighbor searches. By leveraging this method, the script determines proximity based on projected physical separation and velocity differences between galaxies. 

## Features
- Load galaxy catalogs from CSV files. It must contain RA, DEC, and redshift (z) columns.
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
1. Prepare your galaxy catalogs in CSV format. Make sure it has RA (in deg), DEC (in deg) and redshift (z) columns.
2. Ensure the CSV files are accessible from the directory where you intend to run the script.
3. Run the script by specifying the paths to your input files and the desired output file directly from the command line. Additional optional parameters allow for further customization.
   ```bash
   python GalacticNeighborsFinder.py <RQE_catalog_path> <SDSS_catalog_path> <output_file_path> [--max_neighbors MAX_NEIGHBORS] [--R_max R_MAX] [--Delta_v_max DELTA_V_MAX]
   ```
- <RQE_catalog_path>: File path to the RQE galaxy catalog CSV file.
- <SDSS_catalog_path>: File path to the SDSS galaxy catalog CSV file.
- <output_file_path>: File path where the output CSV file with proximity scores will be saved.
- --max_neighbors MAX_NEIGHBORS: Optional. Maximum number of neighbors to consider (default: 500).
- --R_max R_MAX: Optional. Maximum projected physical separation (in kpc) between neighbors (default: 5000).
- --Delta_v_max DELTA_V_MAX: Optional. Maximum velocity difference (in km/s) between neighbors (default: 3000).
  
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
