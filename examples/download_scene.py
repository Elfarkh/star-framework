from datetime import datetime
import geopandas as gpd
from shapely.geometry import box

from star.sensors.landsat import Landsat

aoi = gpd.GeoDataFrame(
    geometry=[box(-8.55, 31.55, -8.35, 31.75)],
    crs="EPSG:4326",
)

landsat = Landsat()

scenes = landsat.search(
    aoi=aoi,
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 12, 31),
)

scene = landsat.download(scenes[0])

print(scene.local_path)
