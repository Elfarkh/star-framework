"""
Test Sentinel-3 / Landsat calibration pairing.
"""

from datetime import datetime

import geopandas as gpd
import numpy as np
from shapely.geometry import box

from star.sensors.landsat import Landsat
from star.sensors.sentinel3 import Sentinel3


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 1, 31)

MAX_TIME_DIFFERENCE_MINUTES = 15


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
# Find Landsat processing tile
# ---------------------------------------------------------

tile = landsat.find_tile(aoi)

tile_geometry = landsat._tile_geometry(tile)

print("Landsat tile:", tile)


# ---------------------------------------------------------
# Find Landsat scenes
# ---------------------------------------------------------

landsat_scenes = landsat.search(
    aoi=aoi,
    start_date=START_DATE,
    end_date=END_DATE,
)

if not landsat_scenes:
    raise RuntimeError(
        "No Landsat scenes found."
    )

landsat_scene = landsat_scenes[0]

print(
    "Landsat acquisition:",
    landsat_scene.acquisition_date,
)


# ---------------------------------------------------------
# Find Sentinel-3 scenes
# ---------------------------------------------------------

sentinel3_scenes = sentinel3.search(
    aoi=aoi,
    start_date=START_DATE,
    end_date=END_DATE,
)

if not sentinel3_scenes:
    raise RuntimeError(
        "No Sentinel-3 scenes found."
    )


# ---------------------------------------------------------
# Select Sentinel-3 acquisition closest to Landsat
# ---------------------------------------------------------

scene = min(
    sentinel3_scenes,
    key=lambda s: abs(
        s.datetime
        - landsat_scene.acquisition_date
    ),
)

time_difference_minutes = abs(
    scene.datetime
    - landsat_scene.acquisition_date
).total_seconds() / 60


print(
    "Closest Sentinel-3 acquisition:",
    scene.datetime,
)

print(
    "Time difference:",
    time_difference_minutes,
    "minutes",
)

print(
    "Valid calibration pair:",
    time_difference_minutes
    <= MAX_TIME_DIFFERENCE_MINUTES,
)


# ---------------------------------------------------------
# Stop if temporal matching is not acceptable
# ---------------------------------------------------------

if (
    time_difference_minutes
    > MAX_TIME_DIFFERENCE_MINUTES
):
    raise RuntimeError(
        "No Sentinel-3 acquisition within "
        f"{MAX_TIME_DIFFERENCE_MINUTES} minutes "
        "of the Landsat acquisition."
    )


# ---------------------------------------------------------
# Download matched scenes
# ---------------------------------------------------------

landsat.download(
    landsat_scene
)

sentinel3.download(
    scene
)


# ---------------------------------------------------------
# Read Landsat LST
# ---------------------------------------------------------

landsat_lst = landsat.usgs_lst(
    landsat_scene
)


# ---------------------------------------------------------
# Create Sentinel-3 LST raster
# ---------------------------------------------------------

sentinel3_lst = sentinel3.lst(
    scene=scene,
    target=landsat_lst,
    geometry=tile_geometry,
)


# ---------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------

valid = np.isfinite(
    sentinel3_lst.data
)

print("\nSentinel-3 LST Raster")

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
    "Valid pixels:",
    np.sum(valid),
)

print(
    "Valid fraction:",
    np.mean(valid),
)

print(
    "LST range:",
    np.nanmin(sentinel3_lst.data),
    np.nanmax(sentinel3_lst.data),
)