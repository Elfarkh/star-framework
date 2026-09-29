"""
STAR dataset.
"""

from dataclasses import dataclass
from typing import Any
from ..raster import Raster


@dataclass
class STARDataset:
    """
    Input dataset for STAR algorithms.
    """

    coarse_lst: Raster
    fine_ndvi: Raster

    reference_lst: Raster | None = None

    weather: Any | None = None