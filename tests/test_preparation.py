from datetime import datetime

import geopandas as gpd
from shapely.geometry import box

from star.sensors.landsat import Landsat
from star.core.star_dataset import STARDataset
from star.algorithms.star_lst.preparation import prepare


def test_prepare():

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

    landsat.download(scene)

    dataset = STARDataset(
        coarse_lst=landsat.usgs_lst(scene),
        fine_ndvi=landsat.ndvi(scene),
    )

    prepared = prepare(dataset)

    assert prepared.aggregated_ndvi is not None

    assert prepared.calibration_mask is not None

    assert prepared.samples is not None

    assert prepared.samples.ndvi.size > 0

    assert prepared.samples.lst.size > 0

    assert prepared.samples.ndvi.shape == prepared.samples.lst.shape