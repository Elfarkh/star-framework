import geopandas as gpd
from shapely.geometry import box

from star.sensors.landsat import Landsat


def test_find_tile():

    aoi = gpd.GeoDataFrame(
        geometry=[box(-8.55, 31.55, -8.35, 31.75)],
        crs="EPSG:4326",
    )

    landsat = Landsat()

    tile = landsat.find_tile(aoi)

    assert tile.path == 202
    assert tile.row == 38
