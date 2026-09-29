"""
STAR-LST data preparation.
"""

import numpy as np

from ...core.raster import Raster
from ...core.star_dataset import STARDataset
from ...utils.resampling import aggregate

from .datasets import (
    CalibrationSamples,
    PreparedDataset,
)

def prepare(
    dataset: STARDataset,
) -> PreparedDataset:
    """
    Prepare the input dataset for STAR-LST.
    """

    aggregated_ndvi = aggregate(
        source=dataset.fine_ndvi,
        target=dataset.coarse_lst,
    )

    prepared = PreparedDataset(
        coarse_lst=dataset.coarse_lst,
        fine_ndvi=dataset.fine_ndvi,
        reference_lst=dataset.reference_lst,
        weather=dataset.weather,
        aggregated_ndvi=aggregated_ndvi,
    )

    return select_calibration_samples(prepared)

def select_calibration_samples(
    prepared: PreparedDataset,
) -> PreparedDataset:
    """
    Select pixels used to calibrate STAR-LST.
    """

    coarse_lst = prepared.coarse_lst.data.flatten()

    aggregated_ndvi = prepared.aggregated_ndvi.data.flatten()

    calibration_mask = (
        (~np.isnan(aggregated_ndvi))
        &
        (~np.isnan(coarse_lst))
        &
        (aggregated_ndvi > 0)
        &
        (coarse_lst > 260)
    )

    prepared.calibration_mask = Raster(
        data=calibration_mask.reshape(prepared.coarse_lst.shape),
        profile=prepared.coarse_lst.profile.copy(),
    )

    prepared.samples = CalibrationSamples(
        ndvi=aggregated_ndvi[calibration_mask],
        lst=coarse_lst[calibration_mask],
    )

    return prepared