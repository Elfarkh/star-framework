"""
Raster resampling utilities.
"""

import numpy as np

from rasterio.warp import reproject, Resampling

from ..core.raster import Raster


def resample(
    source: Raster,
    target: Raster,
    method: Resampling,
) -> Raster:
    """
    Resample a raster onto the grid of another raster.
    """

    destination = np.empty(
        target.shape,
        dtype="float32",
    )

    reproject(
        source=source.data,
        destination=destination,
        src_transform=source.transform,
        src_crs=source.crs,
        dst_transform=target.transform,
        dst_crs=target.crs,
        src_nodata=np.nan,
        dst_nodata=np.nan,
        resampling=method,
    )

    return Raster(
        data=destination,
        profile=target.profile.copy(),
    )

def aggregate(
    source: Raster,
    target: Raster,
) -> Raster:
    """
    Aggregate a raster to the grid of another raster.
    """

    return resample(
        source=source,
        target=target,
        method=Resampling.average,
    )