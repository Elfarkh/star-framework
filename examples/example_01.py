from datetime import datetime
from pathlib import Path

from star.sensors.landsat_scene import LandsatScene


scene = LandsatScene(
    scene_id="LC09_199036_20260515",
    satellite="Landsat-9",
    acquisition_date=datetime(2026, 5, 15),
    path=199,
    row=36,
    cloud_cover=8.4,
    folder=Path("/data/landsat"),
)

print(scene)
