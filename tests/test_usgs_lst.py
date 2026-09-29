from datetime import datetime

import geopandas as gpd
from shapely.geometry import box

from star.sensors.landsat import Landsat


def test_usgs_lst():

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

    lst = landsat.usgs_lst(scene)

    assert lst.shape == (7751, 7611)

    assert 240 < lst.min < 250
    assert 300 < lst.max < 310