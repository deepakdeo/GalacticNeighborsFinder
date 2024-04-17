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
