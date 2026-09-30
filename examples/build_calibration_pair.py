"""
Build and inspect one real STAR-LST calibration pair.
"""

import geopandas as gpd
import numpy as np
from shapely.geometry import box

from star.core.star_dataset import STARDataset
from star.sensors.landsat import Landsat
from star.sensors.sentinel3 import Sentinel3

from star.algorithms.star_lst.calibration import (
    find_calibration_pairs,
)
from star.algorithms.star_lst.preparation import prepare


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

START_YEAR = 2025


# ---------------------------------------------------------
# Area of interest
# ---------------------------------------------------------

aoi = gpd.GeoDataFrame(
    geometry=[
        box(
            -8.55,
            31.55,
            -8.35,
            31.75,
        )
    ],
    crs="EPSG:4326",
)


# ---------------------------------------------------------
# Initialize sensors
# ---------------------------------------------------------

landsat = Landsat()
sentinel3 = Sentinel3()


# ---------------------------------------------------------
# Find calibration pairs
# ---------------------------------------------------------

pairs = find_calibration_pairs(
    aoi=aoi,
    landsat=landsat,
    sentinel3=sentinel3,
    start_year=START_YEAR,
)

if not pairs:
    raise RuntimeError(
        "No valid calibration pairs found."
    )


# ---------------------------------------------------------
# Use first selected pair
# ---------------------------------------------------------

pair = pairs[0]

print(
    "\nCalibration date:",
    pair.landsat.acquisition_date,
)

print(
    "Time difference:",
    pair.time_difference_minutes,
    "minutes",
)


# ---------------------------------------------------------
# Determine processing domain
# ---------------------------------------------------------

tile = landsat.find_tile(aoi)

tile_geometry = landsat._tile_geometry(
    tile
)

print(
    "Landsat tile:",
    tile,
)


# ---------------------------------------------------------
# Download Landsat
# ---------------------------------------------------------

landsat.download(
    pair.landsat
)


# ---------------------------------------------------------
# Landsat fine-resolution products
# ---------------------------------------------------------

landsat_ndvi = landsat.ndvi(
    pair.landsat
)

landsat_lst = landsat.usgs_lst(
    pair.landsat
)


# ---------------------------------------------------------
# Sentinel-3 coarse-resolution LST
# ---------------------------------------------------------

sentinel3.download(
    pair.sentinel3
)

sentinel3_lst = sentinel3.lst(
    scene=pair.sentinel3,
    target=landsat_lst,
    geometry=tile_geometry,
)


# ---------------------------------------------------------
# Build STAR dataset
# ---------------------------------------------------------

dataset = STARDataset(
    coarse_lst=sentinel3_lst,
    fine_ndvi=landsat_ndvi,
    reference_lst=landsat_lst,
)


# ---------------------------------------------------------
# Prepare STAR-LST calibration data
# ---------------------------------------------------------

prepared = prepare(
    dataset
)


# ---------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("STAR-LST CALIBRATION PAIR")
print("=" * 60)


print("\nSentinel-3 LST")

print(
    "Shape:",
    sentinel3_lst.shape,
)

print(
    "CRS:",
    sentinel3_lst.crs,
)

print(
    "Resolution:",
    sentinel3_lst.transform.a,
)

print(
    "Valid fraction:",
    np.mean(
        np.isfinite(
            sentinel3_lst.data
        )
    ),
)

print(
    "Range:",
    np.nanmin(
        sentinel3_lst.data
    ),
    np.nanmax(
        sentinel3_lst.data
    ),
)


print("\nLandsat NDVI")

print(
    "Shape:",
    landsat_ndvi.shape,
)

print(
    "CRS:",
    landsat_ndvi.crs,
)

print(
    "Range:",
    np.nanmin(
        landsat_ndvi.data
    ),
    np.nanmax(
        landsat_ndvi.data
    ),
)


print("\nAggregated Landsat NDVI")

print(
    "Shape:",
    prepared.aggregated_ndvi.shape,
)

print(
    "CRS:",
    prepared.aggregated_ndvi.crs,
)

print(
    "Range:",
    np.nanmin(
        prepared.aggregated_ndvi.data
    ),
    np.nanmax(
        prepared.aggregated_ndvi.data
    ),
)


print("\nLandsat reference LST")

print(
    "Shape:",
    landsat_lst.shape,
)

print(
    "CRS:",
    landsat_lst.crs,
)

print(
    "Range:",
    np.nanmin(
        landsat_lst.data
    ),
    np.nanmax(
        landsat_lst.data
    ),
)


print("\nCalibration samples")

print(
    "Number:",
    len(
        prepared.samples.ndvi
    ),
)

print(
    "NDVI range:",
    prepared.samples.ndvi.min(),
    prepared.samples.ndvi.max(),
)

print(
    "LST range:",
    prepared.samples.lst.min(),
    prepared.samples.lst.max(),
)