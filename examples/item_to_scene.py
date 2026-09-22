from datetime import datetime

from star.catalogs.stac import STAC
from star.sensors.landsat import Landsat

bbox = [-8.55, 31.55, -8.35, 31.75]

catalog = STAC()
landsat = Landsat()

items = catalog.search(
    collection="landsat-c2-l2",
    bbox=bbox,
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 12, 31),
)

scene = landsat._item_to_scene(items[0])

print(scene)
