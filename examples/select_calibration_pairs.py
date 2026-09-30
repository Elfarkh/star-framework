"""
Select STAR-LST calibration pairs.
"""

import geopandas as gpd
from shapely.geometry import box

from star.sensors.landsat import Landsat
from star.sensors.sentinel3 import Sentinel3
from star.algorithms.star_lst.calibration import (
    find_calibration_pairs,
)


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


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("SELECTED CALIBRATION PAIRS")
print("=" * 60)

for pair in pairs:

    print(
        pair.landsat.acquisition_date.date(),
        f"Q{pair.quarter}",
        f"Δt={pair.time_difference_minutes:.1f} min",
    )


print(
    "\nTotal selected:",
    len(pairs),
)


for quarter in range(1, 5):

    count = sum(
        pair.quarter == quarter
        for pair in pairs
    )

    print(
        f"Q{quarter}:",
        count,
    )