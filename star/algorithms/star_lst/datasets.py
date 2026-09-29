"""
STAR-LST datasets.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from ...core.raster import Raster
from ...core.star_dataset import STARDataset

@dataclass
class CalibrationSamples:
    """
    Calibration samples used by STAR-LST.
    """

    ndvi: np.ndarray

    lst: np.ndarray

@dataclass
class PreparedDataset(STARDataset):
    """
    Dataset after preparation.
    """

    aggregated_ndvi: Optional[Raster] = None

    calibration_mask: Optional[Raster] = None

    samples: Optional[CalibrationSamples] = None


@dataclass
class TriangleDataset(PreparedDataset):
    """
    Dataset after triangle construction.
    """

    ndvi_min: Optional[float] = None

    ndvi_max: Optional[float] = None

    lst_min: Optional[float] = None

    p1: Optional[tuple[float, float]] = None

    ndvi_edges: Optional[np.ndarray] = None

    triangles: Optional[list] = None

    triangle_ids: Optional[np.ndarray] = None


@dataclass
class RegressionDataset(TriangleDataset):
    """
    Dataset after local regression.
    """

    regression_models: Optional[dict] = None


@dataclass
class PredictionDataset(RegressionDataset):
    """
    Dataset after prediction.
    """

    predicted_lst: Optional[Raster] = None