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
class TriangleGeometry:
    """
    Geometry of the STAR-LST triangular partition.
    """

    ndvi_min: float

    ndvi_max: float

    lst_baseline: float

    dry_edge_anchor: DryEdgeAnchor

    ndvi_edges: np.ndarray

    triangles: list[Triangle] | None = None

@dataclass
class TriangleDataset(PreparedDataset):

    geometry: TriangleGeometry | None = None

    triangle_ids: np.ndarray | None = None

@dataclass
class Triangle:
    """
    One STAR-LST triangle.
    """

    apex: DryEdgeAnchor

    left: tuple[float, float]

    right: tuple[float, float]

@dataclass
class LocalRegression:
    """
    Local regression model associated with one triangle.
    """

    triangle_id: int

    model: LinearRegression

@dataclass
class RegressionDataset(TriangleDataset):
    """
    Dataset after local regression.
    """

    regressions: list[LocalRegression] | None = None


@dataclass
class PredictionDataset(RegressionDataset):
    """
    Dataset after prediction.
    """

    predicted_lst: Optional[Raster] = None