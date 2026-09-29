from datetime import datetime

import numpy as np
import geopandas as gpd
from shapely.geometry import box

from star.sensors.landsat import Landsat

aoi = gpd.GeoDataFrame(
    geometry=[box(-8.55, 31.55, -8.35, 31.75)],
    crs="EPSG:4326",
)

landsat = Landsat()

scene = landsat.search(
    aoi=aoi,
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 12, 31),
)[0]

scene = landsat.download(scene)

qa = landsat.read(scene, "qa_pixel")

value = int(np.unique(qa.data)[1])

print(value)
print(bin(value))